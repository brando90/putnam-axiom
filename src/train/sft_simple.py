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
    train_dataset = load_math_style_dataset('Putnam-AXIOM/putnam-axiom-dataset', tok, config.get('max_seq_length', 512), end=53, split='func_original_53_10_30_2024')
    print(f'{len(train_dataset)=}')
    eval_dataset = load_math_style_dataset('Putnam-AXIOM/putnam-axiom-dataset', tok, config.get('max_seq_length', 512), end=265, split='func_variations_265_10_30_2024')

    # train model
    # max_steps = 50  # Limit fine-tuning to a few steps
    today: str = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss')
    training_args = SFTConfig(
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        num_train_epochs=config.get('num_train_epochs', 3),
        gradient_accumulation_steps=config.get('gradient_accumulation_steps', 1),
        max_seq_length=config.get('max_seq_length', 512),
        save_strategy=config.get('save_strategy', 'epoch'),
        eval_on_start=config.get('on_start', True),
        evaluation_strategy=config.get('evaluation_strategy', 'steps'),  # Evaluate at regular intervals
        eval_steps=config.get('eval_steps', 5),  # Evaluate every 5 steps
        logging_steps=config.get('logging_steps', 5),
        output_dir=os.path.expanduser(f"~/data/runs_logic_cont/run_{config.get('today', today)}"),
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

def _main(**kwargs):
    from datetime import datetime
    today = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss') # eg '2024_m01_d22_t13h_00m_30s'
    run_name = f'{today}' 
    run = wandb.init(mode=kwargs.get('mode', 'dryrun'), project="putnam-axiom", name=run_name, save_code=True, config=kwargs)
    # wandb.config.update()
    kwargs = kwargs | {'today': today}
    # main(**kwargs)
    main(kwargs)
    print(f'{run.get_url()=}')
    wandb.finish()

if __name__ == "__main__":
    import time
    start_time = time.time()
    fire.Fire(_main)
    print(f"Time taken: {time.time() - start_time:.2f} seconds, or {(time.time() - start_time) / 60:.2f} minutes, or {(time.time() - start_time) / 3600:.2f} hours.\a")
