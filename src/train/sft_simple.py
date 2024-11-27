from datetime import datetime
from typing import Optional
import torch
from transformers import PushToHubCallback
from trl import SFTConfig, SFTTrainer
import os
import fire
import wandb
import sys

from train.data import load_math_style_dataset
import train.models

def main(config: Optional[dict] = {}):
    # hf login
    from huggingface_hub import login
    token = open(os.path.expanduser("~/keys/master_hf_token.txt")).read().strip()
    login(token=token)

    # get model
    model, tok = train.models.load_mdl_and_tok(config.get('pretrained_model_name_or_path', 'google/gemma-2-2b')) 

    # load datasets
    ds_name_or_path = config.get('ds_name_or_path', 'Putnam-AXIOM/putnam-axiom-dataset')
    train_split, val_split = config.get('train_split', 'func_original_53_10_30_2024'), config.get('val_split', 'func_variations_265_11_23_2024')
    train_dataset = load_math_style_dataset(ds_name_or_path, tok, config.get('max_seq_length', 500), end=53, split=train_split)
    eval_dataset = load_math_style_dataset(ds_name_or_path, tok, config.get('max_seq_length', 500), end=265, split=val_split)
    print(f'{len(train_dataset)=}\n{len(eval_dataset)=}')
    wandb.config.update({'dataset': f'{ds_name_or_path} ({train_split=} {val_split=})'})

    # load datasets
    # print(f'brando/hendrycks_math')
    # train_dataset = load_math_style_dataset('brando/hendrycks_math', tok, config.get('max_seq_length', 700), end=5000, split='test')
    # print(f'{len(train_dataset)=}')
    # eval_dataset = load_math_style_dataset('brando/hendrycks_math', tok, config.get('max_seq_length', 700), end=7500, split='train')
    # print(f'{len(eval_dataset)=}')
    # wandb.config.update({'dataset': 'brando/hendrycks_math (test)'})

    # train model
    # max_steps = 50  # Limit fine-tuning to a few steps
    today: str = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss')
    output_dir: str = os.path.expanduser(f"~/data/runs_logic_cont/run_{config.get('today', today)}")
    print(f'{output_dir=}')
    training_args = SFTConfig(
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        # fp16=False,
        num_train_epochs=config.get('num_train_epochs', 10),
        gradient_accumulation_steps=config.get('gradient_accumulation_steps', 1),
        max_seq_length=config.get('max_seq_length', 500),
        save_strategy=config.get('save_strategy', 'epoch'),
        eval_on_start=config.get('on_start', True),
        evaluation_strategy=config.get('evaluation_strategy', 'steps'),  # Evaluate at regular intervals
        eval_steps=config.get('eval_steps', 5),  # Evaluate every 5 steps
        logging_steps=config.get('logging_steps', 5),
        output_dir=output_dir,
        per_device_train_batch_size=config.get('batch_size', 8),
    )
    # optimizer_grouped_parameters = [{'params': [p for p in model.lm_head.parameters()], 'weight_decay': 1e-4}]
    optimizer_grouped_parameters = [{'params': [p for p in model.parameters()], 'weight_decay': 1e-4}]
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=config.get('learning_rate', 8e-6))
    scheduler = None  # Optional scheduler (not used for simplicity)
    trainer = SFTTrainer(
        model=model,
        tokenizer=tok,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        args=training_args,
        optimizers=(optimizer, scheduler),
        # callbacks=[PushToHubCallback(repo_id="Putnam-AXIOM", private_repo=True)],
    )
    print(f"\nStarting fine-tuning...")
    trainer.train()
    return os.path.expanduser(output_dir)

import os
import subprocess

def run_eval_logic_contamination(output_dir: str):
    """
    Runs the eval_logic_contamination.py script with the specified output directory.

    Args:
        output_dir (str): The directory where the model is saved, expanded using `os.path.expanduser`.
    """
    output_dir = os.path.expanduser(output_dir)  # Ensure `output_dir` is expanded
    subprocess_cmd = [
        "bash", "-c",
        f"""
        conda activate putnam_axiom && \
        export task="putnam_axiom_53" && \
        export model_name_or_path="{output_dir}" && \
        export mode="online" && \
        python ~/putnam-axiom/src/eval_logic_contamination.py --task ${{task}} --mode ${{mode}} --model_name_or_path ${{model_name_or_path}}
        """
    ]

    # Run subprocess
    print("Running eval_logic_contamination.py...")
    subprocess.run(subprocess_cmd, check=True)
    print("Evaluation complete!")

def _main(**kwargs):
    from datetime import datetime
    today = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss') # eg '2024_m01_d22_t13h_00m_30s'
    run_name = f'{today}' 
    run = wandb.init(mode=kwargs.get('mode', 'dryrun'), project="putnam-axiom", name=run_name, save_code=True, config=kwargs)
    # wandb.config.update()
    kwargs = kwargs | {'today': today}
    # main(**kwargs)
    output_dir = main(kwargs)
    run_eval_logic_contamination(output_dir)
    print(f'{run.get_url()=}')
    wandb.finish()

if __name__ == "__main__":
    import time
    start_time = time.time()
    fire.Fire(_main)
    print(f"Time taken: {time.time() - start_time:.2f} seconds, or {(time.time() - start_time) / 60:.2f} minutes, or {(time.time() - start_time) / 3600:.2f} hours.\a")
