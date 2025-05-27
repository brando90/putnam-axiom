import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling, TrainerCallback, TrainerControl, TrainerState
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, PeftModel
import os
from pathlib import Path
from deepspeed.utils.zero_to_fp32 import get_fp32_state_dict_from_zero_checkpoint
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    trust_remote_code=True
)
model = model.cpu()
state_dict = get_fp32_state_dict_from_zero_checkpoint(f"ft_output/{model_name}/checkpoint-300")
model.load_state_dict(state_dict, strict=False)
model.save_pretrained(f"putnam-axiom/src/models/sft_{model_name}")

