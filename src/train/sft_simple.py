from typing import Optional
import torch
from trl import SFTConfig, SFTTrainer
import os
import fire
import wandb

from src.train.data import load_math_style_dataset
import src.train.models

def main(config: Optional[dict] = {}):
    # hf login
    from huggingface_hub import login
    token = open(os.path.expanduser("~/keys/master_hf_token.txt")).read().strip()
    login(token=token)

    # get model
    model, tok = src.train.models.load_mdl_and_tok(config.get('pretrained_model_name_or_path', 'google/gemma-2-2b')) 

    # load datasets
    train_dataset = load_math_style_dataset('Putnam-AXIOM/putnam-axiom-dataset', tok, config.get('max_seq_length', 512), 53, 'func_original_53_10_30_2024')
    eval_dataset = load_math_style_dataset('Putnam-AXIOM/putnam-axiom-dataset', tok, config.get('max_seq_length', 512), 265, 'func_variations_265_10_30_2024')

    # train model
    max_steps = 50  # Limit fine-tuning to a few steps
    training_args = SFTConfig(
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        max_steps=max_steps,
        gradient_accumulation_steps=config.get('gradient_accumulation_steps', 1),
        max_seq_length=config.get('max_seq_length', 512),
        output_dir=os.path.expanduser("~/tmp"),
        per_device_train_batch_size=8,
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
    )
    print(f"\nStarting fine-tuning for {max_steps} steps...")
    trainer.train()

def _main(**kwargs):
    from datetime import datetime
    today = datetime.now().strftime('m%m-d%d-%Y-t%Hh_%Mm_%Ss') # eg 'm10-d29-2024-t15h_07m_43s'
    run_name = f'{today}' 
    run = wandb.init(mode=kwargs.get('mode', 'dryrun'), project="beyond-scale-2", name=run_name, save_code=True, config=kwargs)
    # wandb.config.update()
    main(**kwargs)
    print(f'{run.get_url()=}')
    wandb.finish()

if __name__ == "__main__":
    import time
    start_time = time.time()
    fire.Fire(_main)
    print(f"Time taken: {time.time() - start_time:.2f} seconds, or {(time.time() - start_time) / 60:.2f} minutes, or {(time.time() - start_time) / 3600:.2f} hours.\a")
