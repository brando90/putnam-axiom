# ref: https://chatgpt.com/c/673ea80c-7ce0-8001-a42c-b47891b0f0ed
from datetime import datetime
from transformers import PushToHubCallback, TrainerCallback
import os
import wandb
from tfa import compute_tfa

# class SaveAndPushCallback(TrainerCallback):
#     def __init__(self, base_repo_name, private=True):
#         self.base_repo_name = base_repo_name
#         self.private = private

#     def on_epoch_end(self, args, state, control, **kwargs):
#         epoch = int(state.epoch)
#         repo_name = f"{self.base_repo_name}-epoch{epoch}"
#         output_dir = os.path.join(args.output_dir, f"epoch{epoch}")
#         trainer = kwargs['trainer']
        
#         # Save the model locally for this epoch
#         trainer.save_model(output_dir)
#         print(f"Model for epoch {epoch} saved locally at {output_dir}.")
        
#         # Push the model to the Hugging Face Hub
#         print(f"Pushing model for epoch {epoch} to Hugging Face Hub as {repo_name}...")
#         trainer.model.push_to_hub(repo_name, private=self.private)
#         print(f"Model for epoch {epoch} pushed to Hugging Face Hub as {repo_name}.")

class TFACallback(TrainerCallback):
    def __init__(self, tokenizer, train_input_texts, eval_input_texts=None):
        """
        A custom callback to compute and log Teacher-Forced Accuracy (TFA) for both training and evaluation datasets.

        Parameters:
            tokenizer: The tokenizer corresponding to the model.
            train_input_texts: List of input texts for computing TFA during training.
            eval_input_texts: List of input texts for computing TFA during evaluation (optional).
        """
        self.tokenizer = tokenizer
        self.train_input_texts = train_input_texts
        self.eval_input_texts = eval_input_texts or train_input_texts  # Use training inputs if evaluation inputs are not provided

    def on_step_end(self, args, state, control, **kwargs):
        """
        Compute and log TFA for training at the end of each step.
        """
        trainer = kwargs["trainer"]
        model = trainer.model
        tfa_score = compute_tfa(model, self.tokenizer, self.train_input_texts)
        
        # Log training TFA to console and W&B
        print(f"Step {state.global_step}: TFA (train) = {tfa_score:.4f}")
        if trainer.is_world_process_zero():
            wandb.log({"TFA (train)": tfa_score, "step": state.global_step})

    def on_evaluate(self, args, state, control, **kwargs):
        """
        Compute and log TFA for evaluation during evaluation phases.
        """
        trainer = kwargs["trainer"]
        model = trainer.model
        tfa_score = compute_tfa(model, self.tokenizer, self.eval_input_texts)
        
        # Log evaluation TFA to console and W&B
        print(f"Evaluation at step {state.global_step}: TFA (eval) = {tfa_score:.4f}")
        if trainer.is_world_process_zero():
            wandb.log({"TFA (eval)": tfa_score, "step": state.global_step})
