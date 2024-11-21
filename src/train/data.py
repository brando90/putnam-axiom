
import sys
from typing import Optional
from datasets import load_dataset
import os
from transformers import AutoTokenizer
import torch

def get_lm_examples_1st_eos_mask_remaining_eos(
        examples,
        tokenizer: AutoTokenizer, 
        remove_to_long_seqs: bool = False,
        debug: bool = False,
        ) -> dict[str, torch.Tensor]:
    """ 
    Train only on first occurence of eos. The remaining eos are masked out. If 
        - train up to 1st ocurrence of eos token, mask out the rest of the eos tokens.
        - drop or not seqs that are too long, i.e., have no eos token.
    
    Assumes: pad == eos

    ref: https://stackoverflow.com/questions/76633368/how-does-one-set-the-pad-token-correctly-not-to-eos-during-fine-tuning-to-avoi
    """
    # assert tokenizer.pad_token == tokenizer.eos_token, 'Error: if eos_token and pad_token are not the same, this function doesnt work. This function tries to mask the '
    # - Get lm example
    seq_length: int = examples['input_ids'].size(0)
    print(f'{examples["input_ids"].size()=}, {seq_length=}') if debug else None
    examples["labels"] = examples["input_ids"].clone()  # labels is hardcoded in HF so put it!
    eos_token_id = tokenizer.eos_token_id
    print(f'{tokenizer.pad_token_id=}, {tokenizer.eos_token_id=}') if debug else None
    seqs_to_drop: list[int] = [] # store idx to drop (to long), we don't want to modify the two lists at the same time as we are looping through them
    for idx, input_ids in enumerate(examples["input_ids"]):
        assert len(input_ids.size()) == 1, 'Should be 1 example at a time in the batch or set of examples (e.g., 1 of 1000 if batched=True).'
        # Find all occurrences of eos_token
        _eos_positions = (input_ids == eos_token_id).nonzero() # get idxs for eos as a [z, 1] tensor or [z, n] for n dim tensors since all idxs for eos are needed to locate it. 
        eos_positions = _eos_positions[:, 0] # get the [z] values for eos
        if eos_positions.nelement() > 0:  # Check if eos_token is present --> if yes then make sure to train on only 1st, att mask eos after and not train on those eos's either
            first_eos_position = eos_positions[0]
            examples["attention_mask"][idx, first_eos_position] = 1  # Set the mask value to 1
            examples["attention_mask"][idx, first_eos_position + 1:] = 0 
            assert examples["labels"][idx, first_eos_position] == eos_token_id, f"The label for the first eos_token is not eos, it's {eos_token_id=}"
            # after first eos token mask everything (eos AND pad, hopefully that's all there but we can sanity check later)
            examples["labels"][idx, first_eos_position + 1:] = -100
        elif remove_to_long_seqs:
            assert eos_positions.nelement() == 0, 'Error: there should be no eos if this if stmt is exexuted.'
            # record to drop this seq, has no eos so too long + flag says to drop it
            seqs_to_drop.append(idx)
        else:
            # no eos should be present at all
            assert sum(examples["labels"][idx] == -100) == 0, f"If it's too long then no pad as eos token present but got some pad token to ignore incorrectly:\n{examples['labels']=}"
            assert sum(examples["attention_mask"][idx] == 0) == 0, f"If it's too long then no pad as eos token present but got some pad token to ignore incorrectly:\n{examples['input_ids']=}"
            pass # nop: no eos in seq so too long, but keep it for training anyway
    # -- Drop seqs with no eos
    if seqs_to_drop:
        examples["input_ids"] = torch.stack([input_ids for idx, input_ids in enumerate(examples["input_ids"]) if idx not in seqs_to_drop])
        examples["attention_mask"] = torch.stack([mask for idx, mask in enumerate(examples["attention_mask"]) if idx not in seqs_to_drop])
        examples["labels"] = torch.stack([labels for idx, labels in enumerate(examples["labels"]) if idx not in seqs_to_drop])
    return examples

def load_math_style_dataset(
        ds_path: str, 
        tokenizer, 
        max_length: int, 
        # num_proc: Optional[int] = None, # for .map
        num_proc: Optional[int] = os.cpu_count(), # for .map
        shuffle: bool = False, # but slows things down
        truncation: bool = True, 
        seed: int = 0,
        end: Optional[int] = None, 
        split: Optional[str] = None,
        batched: bool = True
        ):
    print(f'{num_proc=}')
    end: int = end if end is not None else sys.maxsize
    ds = load_dataset(ds_path, split=split)
    ds = ds.shuffle(seed=seed) if shuffle else ds
    try:
        ds = ds.select(range(end)) if end is not None else ds
    except Exception as e:
        ds = ds.take(end) if end is not None else ds
    # - Step1: to train str
    raw_str_2_train_str = lambda examples : {'text': [f'problem: {prob}\n\nsolution: {sol}' for prob, sol in zip(examples['problem'], examples['solution'])]}
    train_str_ds = ds.map(raw_str_2_train_str, batched=batched, num_proc=num_proc)
    # - Step2: to train tokenized ds
    tok_ds = train_str_ds.with_format('torch')  
    tokenize_function = lambda examples: tokenizer(examples['text'], padding='max_length', max_length=max_length, truncation=truncation, return_tensors='pt')
    tok_ds = tok_ds.map(tokenize_function, batched=batched, remove_columns=tok_ds.column_names, num_proc=num_proc)
    # - Step3: to lm dataset
    get_lm_examples_function = lambda examples : get_lm_examples_1st_eos_mask_remaining_eos(examples, tokenizer)
    lm_ds = tok_ds.map(get_lm_examples_function, batched=batched, num_proc=num_proc)
    return lm_ds