from datetime import datetime
from typing import Optional
import random
import torch
from transformers import PushToHubCallback
from transformers import get_cosine_schedule_with_warmup
from trl import SFTConfig, SFTTrainer
import os
import fire
import wandb
import sys

from train.callbacks import GenCallbackWithHFGenerate
from train.data import load_math_style_dataset, print_first_example_after_decode
import train.models

from train.utils import seed_everything

def main(**config):
    # -- Seed everything
    seed_everything(seed=config.get('seed', 0))
    
    # -- HF login
    from huggingface_hub import login
    token = open(os.path.expanduser("~/keys/master_hf_token.txt")).read().strip()
    login(token=token)

    # -- Get model
    model, tok = train.models.load_mdl_and_tok(config.get('pretrained_model_name_or_path', 'google/gemma-2-2b')) 
    # model, tok = train.models.load_mdl_and_tok(config.get('pretrained_model_name_or_path', 'meta-llama/Llama-3.1-8B')) 

    # -- Load datasets
    ds_name_or_path = config.get('ds_name_or_path', 'Putnam-AXIOM/putnam-axiom-dataset')
    train_split, val_split = config.get('train_split', 'func_original_53_10_30_2024'), config.get('val_split', 'func_variations_265_11_23_2024')
    print(f'\n---> {ds_name_or_path=} {train_split=} {val_split=}\n')
    train_dataset = load_math_style_dataset(ds_name_or_path, tok, config.get('max_seq_length', 512), end=1, split=train_split)
    print_first_example_after_decode(train_dataset, tok)
    # eval_dataset = load_math_style_dataset(ds_name_or_path, tok, config.get('max_seq_length', 512), end=15, split=val_split)
    eval_dataset = train_dataset
    print(f'{len(train_dataset)=}\n{len(eval_dataset)=}')
    wandb.config.update({'dataset': f'{ds_name_or_path} ({train_split=} {val_split=})'})

    # -- Prepare output directory
    today: str = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss')
    output_dir: str = os.path.expanduser(f"~/data/runs_logic_cont/run_{config.get('today', today)}")
    print(f'{output_dir=}')
    
    # Save the initial model and tokenizer as checkpoint-0
    initial_checkpoint_dir = os.path.join(output_dir, "checkpoint-0")
    os.makedirs(initial_checkpoint_dir, exist_ok=True)
    print(f"Saving initial checkpoint and tokenizer at {initial_checkpoint_dir}")
    model.save_pretrained(initial_checkpoint_dir)
    tok.save_pretrained(initial_checkpoint_dir)

    # -- Train model
    # max_steps = 50  # Limit fine-tuning to a few steps
    # os.environ['CUDA_VISIBLE_DEVICES'] = str(random.randint(0, 7))
    # config = {'max_steps': 2, 'eval_steps': 1, 'logging_steps': 1, 
    #           'save_strategy': 'steps', 'save_steps': 1, 'eval_strategy': 'steps'}
    # config = config | {'CUDA_VISIBLE_DEVICES': os.environ.get('CUDA_VISIBLE_DEVICES', 'maybe 0')}
    training_args = SFTConfig(
        max_steps=config.get('max_steps', 30),
        # --
        output_dir=output_dir,
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        # -- logging opts
        save_steps=config.get('save_steps', 5), 
        save_strategy=config.get('save_strategy', 'steps'),
        eval_on_start=config.get('eval_on_start', True),
        evaluation_strategy=config.get('eval_strategy', 'steps'), 
        eval_steps=config.get('eval_steps', 1), 
        logging_first_step=config.get('logging_first_step', True), # Default to False, unsure 100% what this does but looks like a good idea
        logging_strategy=config.get('logging_strategy', 'steps'),
        logging_steps=config.get('logging_steps', 1),
        # --
        num_train_epochs=config.get('num_train_epochs', 10),
        max_seq_length=config.get('max_seq_length', 512),
        per_device_train_batch_size=config.get('batch_size', 2),
        gradient_accumulation_steps=config.get('gradient_accumulation_steps', 2),
    )
    # Calculate Total Steps
    steps_per_epoch = (len(train_dataset) // training_args.per_device_train_batch_size) // training_args.gradient_accumulation_steps
    total_steps = steps_per_epoch * training_args.num_train_epochs
    print(f'{steps_per_epoch=}')

    # Optimizer and Scheduler
    # optimizer_grouped_parameters = [{'params': [p for p in model.parameters()], 'weight_decay': 1e-4}]
    optimizer_grouped_parameters = [{'params': [p for p in model.parameters()], 'weight_decay': 0}]
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=config.get('learning_rate', 1e-5))

    # Add Cosine Learning Rate Scheduler
    # warmup_steps = int(0.01 * total_steps)  # Warm-up for 1% of total steps
    warmup_steps = 0
    scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )
    scheduler = None
    print(f'{total_steps=} {warmup_steps=}')
    trainer = SFTTrainer(
        model=model,
        tokenizer=tok,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        args=training_args,
        optimizers=(optimizer, scheduler),
        callbacks=[GenCallbackWithHFGenerate(model, tok)]
    )
    print(f"\nStarting fine-tuning...")
    trainer.train()
    # - end run
    return os.path.expanduser(output_dir)

def run_eval_logic_contamination(output_dir: str):
    """
    Runs the eval_logic_contamination.py script with the specified output directory.

    Args:
        output_dir (str): The directory where the model is saved, expanded using `os.path.expanduser`.
    """
    import gc
    torch.cuda.empty_cache()
    gc.collect()
    output_dir = os.path.expanduser(output_dir)  # Ensure `output_dir` is expanded 
    from eval_logic_contamination import main
    task='putnam_axiom_53'
    res: dict = main(model_name_or_path=output_dir, task=task)
    print(f'Results for {task=}: {res}')
    print(res)
    # task='putnam_axiom_53' # for debugging
    task='putnam_axiom_variations'
    res: dict = main(model_name_or_path=output_dir, task=task)
    print(f'Results for {task=}: {res}')
    print(res)
    # wandb.run.define_metric("eval/accuracy", step_metric="eval/checkpoint_idx")
    # wandb.run.define_metric("eval/checkpoint_idx") 
    # for idx, acc in [(10,5), (20,10), (30,15)]:
    #     wandb.log({'eval/accuracy': acc, 'eval/checkpoint_idx': idx})

def _main(**kwargs):
    from datetime import datetime
    today = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss') # eg '2024_m01_d22_t13h_00m_30s'
    run_name = f'{today}' 
    kwargs = kwargs | {'today': today}
    # run = wandb.init(mode=kwargs.get('mode', 'dryrun'), project="putnam-axiom", name=run_name, save_code=True, config=kwargs)
    run = wandb.init(mode=kwargs.get('mode', 'online'), project="putnam-axiom", name=run_name, save_code=True, config=kwargs)
    # wandb.run.log_code(f"./{os.path.basename(__file__)}") # maybe logscode immediately # ref: https://stackoverflow.com/questions/79256112/how-to-log-only-the-current-script-file-to-wb-code-panel-immediately
    # wandb.config.update()
    os.environ['CUDA_VISIBLE_DEVICES'] = str(6)
    print("--> WARNING/REMINDER: cude device harcoded in script!\n"*10)
    output_dir = main(**kwargs)
    run_eval_logic_contamination(output_dir)
    # from train.utils import copy_to_dfs
    # copy_to_dfs(output_dir)
    run.alert(title="Run Completed", text=f"Run finished, run url: {run.get_url()}")
    print(f'{run.get_url()=}')
    wandb.finish()

if __name__ == "__main__":
    import time
    start_time = time.time()
    fire.Fire(_main)
    print(f"Time taken: {time.time() - start_time:.2f} seconds, or {(time.time() - start_time) / 60:.2f} minutes, or {(time.time() - start_time) / 3600:.2f} hours.\a")
