import os
import time
import torch
from datasets import Dataset
from unsloth import FastLanguageModel
from transformers import TrainingArguments
from trl import SFTTrainer
from tqdm import tqdm
from pathlib import Path
from typing import Optional
import fire
from pathlib import Path

from train.utils import load_hf_dataset

from pdb import set_trace as st

def formatting_informalization(example, tokenizer, EOS_TOKEN) -> dict:
    # Must add EOS_TOKEN, otherwise your generation will go on forever!
    informalization_prompt = """
    Below is a natural language explanation of a Theorem from the Lean4 Mathlib library.
    {}
    """
    text: str = informalization_prompt.format(example["informalization"]) + EOS_TOKEN
    return {"text": text}

def main(
        # model_name: str = "unsloth/llama-3-8b",
        # model_name: str = "unsloth/Qwen2-1.5B-bnb-4bit",
        model_name: str = "unsloth/Qwen2-1.5B",
        # model_name: str = "unsloth/gemma-2-2b",
        output_dir_train: str = "~/data/runs/{current_date}_run/train",
        train_path: str = "AI4M/leandojo-informalized",
        per_device_train_batch_size: int = 2,
        gradient_accumulation_steps: int = 4,
        num_train_epochs: int = 1,
        learning_rate: float = 2e-4,
        weight_decay: float = 0.01,
        # max_grad_norm: float = 1.0,
        max_length: int = 8192,
        warmup_steps: int = 5,
        use_4bit: bool = False,
        r_lora: int = 16, # rank of B, A and r in alpha/r
        lora_alpha: int = 16, # alpha/r B*A
        # optim="adamw_8bit",
        optim="paged_adamw_32bit",
        logging_steps: int = 1,
        seed: int = 0,
        model_hub_save_name: Optional[str] = None,
        push_to_hub: Optional[bool] = False,
        hf_token: Optional[str] = None,
        packing: bool = False, # Can make training 5x faster for short sequences if False. TODO check why
        end: Optional[int] = None, # 50 is big enough for packing to work/no code crash
        report_to: str = 'none',
    ):
    print('\n\n\n\n---- Unsloth main training')
    print(f'{packing=} {model_name=} {end=}')
    print(f'{learning_rate=} {lora_alpha=} {r_lora=} {lora_alpha/r_lora=}')
    print(f'{logging_steps=}')
    current_date: str = os.environ['DATE'] # export DATE=$(python -c "from datetime import datetime; print(datetime.now().strftime('%m%d%Y_%Ih%Mm%Ss'))")
    output_dir_train: str = os.path.expanduser(output_dir_train).format(current_date=current_date)
    print(f'{output_dir_train=}')
    time.sleep(3) # sleep to give user time to see/copy important info for run
    
    # Load model and tokenizer
    print(f'{use_4bit=}')
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_length,
        dtype=None,  # Auto-detection for Float16/BFloat16
        load_in_4bit=use_4bit,
    )
    print(f'dtype={next(model.parameters()).dtype}')

    # Add LoRA adapters
    model: FastLanguageModel = FastLanguageModel.get_peft_model(
        model=model,
        r=r_lora,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=lora_alpha,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=seed,
        use_rslora=False,
        loftq_config=None,
    )
    # import uutils.evals.boxed_acc_eval
    # uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='unsloth_fast_model', batch_size=10, end=10)

    # - Load the datasets
    print(f'\n- Load the dataset')
    # train_dataset: Dataset = load_hf_dataset(train_path, tokenizer=None, max_length=None) # trl does tokenization
    train_dataset: Dataset = load_hf_dataset(train_path, tokenizer=None, max_length=max_length, end=end) # trl does tokenization
    # formatting_func = lambda example: f'{example}' # Func formats the str before tokenization e.g., "### Question: {question} ### Answer: {answer}"

    # Training arguments
    output_dir_train: Path = Path(output_dir_train).expanduser()
    output_dir_train.mkdir(parents=True, exist_ok=True)
    training_args = TrainingArguments(
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_steps=warmup_steps,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        # max_grad_norm=max_grad_norm,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=logging_steps,
        optim=optim,
        weight_decay=weight_decay,
        lr_scheduler_type="linear",
        seed=seed,
        output_dir=output_dir_train,
        report_to=report_to,
    )
    print(f'{training_args=}')

    # Initialize the Trainer
    print(f'-- Initialize the Trainer')
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        dataset_text_field="text",
        max_seq_length=max_length,
        dataset_num_proc=2,
        packing=packing,
        args=training_args,
    )
    print(f"-- Starting training for {num_train_epochs} epoch(s)...")
    trainer_stats = trainer.train()

    # Show memory usage
    gpu_stats = torch.cuda.get_device_properties(0)
    start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
    used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
    used_percentage = round(used_memory / max_memory * 100, 3)
    lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)

    print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
    print(f"{used_memory} GB of memory reserved.")
    print(f"{used_memory_for_lora} GB used for LoRA.")
    print(f"{used_percentage}% of GPU memory used.")
    print(f"{lora_percentage}% used for training LoRA.")

    # Save the trained model
    if push_to_hub and model_hub_save_name and hf_token:
        print(f'{model_hub_save_name=} (unsloth doesnt have an api to save to a hf repo or hf org etc. so it will be save to your)')
        model.push_to_hub_merged(
            model_hub_save_name,
            tokenizer=tokenizer,
            save_method="merged_16bit",
            token=hf_token,
        )
    else:
        print(f'{output_dir_train=}\n{str(output_dir_train)=}\n{output_dir_train}')
        final_ckpt_path: str = str(output_dir_train / 'merged_16bit')
        print(f'{final_ckpt_path=}\n{str(final_ckpt_path)=}\n{final_ckpt_path}')
        model.save_pretrained_merged(final_ckpt_path, tokenizer, save_method="merged_16bit")

    # -- Do Math Evals
    # import uutils.evals.boxed_acc_eval
    # uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='unsloth_fast_model', batch_size=100, end=100) 
    return output_dir_train

def get_most_recent_ckpt_path(output_dir: str) -> str:
    def get_latest_checkpoint(output_dir) -> str:
        checkpoints: list[str] = [d for d in os.listdir(output_dir) if d.startswith("checkpoint")]
        latest_checkpoint: str = max(checkpoints, key=lambda x: int(x.split("-")[-1]))  # Get the checkpoint with the highest number
        return os.path.join(output_dir, latest_checkpoint)
    get_latest_ckpt: str = get_latest_checkpoint(trainer.args.output_dir)
    return get_latest_ckpt

def do_math_evals(
        ckpt_dir: Path, # usually the output_dir_train from above
    ):
    # DOESN'T WORK 
    print(f'---> DOING MATH EVALS: {do_math_evals=}')
    # print(f'{ckpt_dir=}')
    import time
    start_time = time.time()
    ckpt_dir: Path = ckpt_dir.expanduser()
    model_name: str = str(ckpt_dir / 'checkpoint-5')
    import gc; gc.collect(); import torch; torch.cuda.empty_cache();
    # - Get most recent ckpt path
    # latest_ckpt_path: str = get_most_recent_ckpt_path(ckpt_dir)
    # -- Do Math Evals
    import uutils.evals.boxed_acc_eval
    # model_name: str = os.path.expanduser('~/data/runs/09302024_07h34m20s_run/train/checkpoint-5')
    print(f'{model_name=}')
    uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='unsloth_fast_model', batch_size=100, end=100) 
    # uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='unsloth_fast_model', batch_size=2, end=2) 
    # uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='unsloth_fast_model', batch_size=2, end=2) 
    # uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='pipeline', batch_size=2, end=2) 
    # uutils.evals.boxed_acc_eval.eval_on_four_math_benchmarks(model_name, gen_type='pipeline', batch_size100, end=100) 
    print(f"> Eval Time taken: {time.time() - start_time:.2f} seconds, or {(time.time() - start_time) / 60:.2f} minutes, or {(time.time() - start_time) / 3600:.2f} hours.\a")

if __name__ == "__main__":
    import time
    start_time = time.time()
    output_dir_train: Path = fire.Fire(main)
    # do_math_evals(ckpt_dir=output_dir_train)
    # do_math_evals(ckpt_dir='')
    print(f"Time taken: {time.time() - start_time:.2f} seconds, or {(time.time() - start_time) / 60:.2f} minutes, or {(time.time() - start_time) / 3600:.2f} hours.\a")
