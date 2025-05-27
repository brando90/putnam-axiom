import os
from huggingface_hub import login
import gc
from vllm import LLM, SamplingParams
import lm_eval
from lm_eval import evaluator, tasks, api
from lm_eval.api.model import LM
# from transformers.deepspeed import convert_zero_checkpoint_to_fp32_state_dict
from deepspeed.utils.zero_to_fp32 import get_fp32_state_dict_from_zero_checkpoint
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
from peft import PeftModel

from pathlib import Path
from deepspeed.utils.zero_to_fp32 import get_fp32_state_dict_from_zero_checkpoint

from typing import List, Tuple
import torch
import random
import json
from openai import OpenAI
import anthropic

class MyLM(LM):
    def __init__(self, model = None, batch_size: int = 4):
        self.model = model
        super().__init__()
        self.batch_size = batch_size

    def loglikelihood(self, requests: List) -> List[Tuple[float, bool]]:
        results = []
        for request in requests:
            context, continuation = request.args()
            # Replace this with actual log-likelihood computation using your model
            logprob = self.model.compute_loglikelihood(context, continuation)
            isgreedy = self.model.is_greedy(context, continuation)
            results.append((logprob, isgreedy))
        return results

    def loglikelihood_rolling(self, requests: List) -> List[float]:
        results = []
        for request in requests:
            context, = request.args()
            logprob = self.model.compute_rolling_loglikelihood(context)
            results.append(logprob)
        return results
    
    def generate_until(self, requests: List) -> List[str]:
        results = []
        context = []
        for request in requests:
            # print(request.args[0])
            # exit()
            context.append(request.args[0])
        
        params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
        results = self.model.generate(context, params)
        # print(results)
        # for request in requests:
        #     response = client.chat.completions.create(
        #         model = 'gpt-4o',
        #         messages = [{"role": "user", "content": request.args[0]}],
        #         max_tokens = 2048
        #     )
        #     results.append(response.choices[0].message.content)
        return results

def ensure_vocab_consistency(model_dir: str):
    """
    Make sure config.vocab_size == embed_tokens.weight.shape[0].
    If they don't match, fix the smaller side and re-save.
    """
    
    # Check if the model directory exists and has required files
    if not os.path.exists(model_dir):
        print(f"[ERROR] Model directory {model_dir} does not exist")
        return False
        
    config_path = os.path.join(model_dir, "config.json")
    if not os.path.exists(config_path):
        print(f"[ERROR] config.json not found in {model_dir}")
        return False
    
    # Check for model files
    safetensors_files = [f for f in os.listdir(model_dir) if f.endswith('.safetensors')]
    bin_files = [f for f in os.listdir(model_dir) if f.endswith('.bin')]
    
    if not safetensors_files and not bin_files:
        print(f"[ERROR] No model weight files found in {model_dir}")
        print("Available files:", os.listdir(model_dir))
        return False
    
    try:
        cfg = AutoConfig.from_pretrained(model_dir, trust_remote_code=True)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return False

    try:
        # Try to load weights on CPU with error handling
        print(f"[INFO] Loading model from {model_dir}...")
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float32  # Use float32 for CPU loading
        )
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        print("This might indicate corrupted model files from DeepSpeed training.")
        print("Try re-running the fine-tuning with proper model saving.")
        return False

    embed_weight = model.get_input_embeddings().weight
    embed_rows = embed_weight.shape[0]
    
    print(f"[INFO] Config vocab_size: {cfg.vocab_size}")
    print(f"[INFO] Embedding rows: {embed_rows}")
    print(f"[INFO] Embedding shape: {embed_weight.shape}")

    if embed_rows != cfg.vocab_size:
        print(f"[fix-vocab] mismatch detected → "
              f"config={cfg.vocab_size}  checkpoint={embed_rows}")

        # Update config to match actual embedding size
        cfg.vocab_size = embed_rows

        # Optional: pad to make it divisible by the tensor-parallel size
        tp_size = 4
        if embed_rows % tp_size != 0:
            padded = math.ceil(embed_rows / tp_size) * tp_size
            print(f"[fix-vocab] padding embeddings {embed_rows}→{padded}")
            model.resize_token_embeddings(padded)
            cfg.vocab_size = padded
            embed_rows = padded

        # Save everything back
        print("[INFO] Saving updated config and model...")
        cfg.save_pretrained(model_dir)
        model.save_pretrained(model_dir, safe_serialization=True)

        # Make sure tokenizer is present
        tokenizer_files = ['tokenizer.json', 'tokenizer_config.json']
        missing_tokenizer = any(not os.path.exists(os.path.join(model_dir, f)) for f in tokenizer_files)
        
        if missing_tokenizer:
            print("[fix-vocab] copying base tokenizer to the model dir")
            base_model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"  # Make sure this matches your base model
            tok = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
            tok.save_pretrained(model_dir)
    else:
        print("[fix-vocab] no mismatch – nothing to do")
    
    # Clean up
    del model
    torch.cuda.empty_cache()
    return True

if __name__ == "__main__":
    # # ---------------------------------------
    # # STEP 1: Load the base model and LoRA adapter.
    # # ---------------------------------------
    # Sanity check
    base_model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
    # base_model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    # # ft_model_dir = "./putnam-axiom/src/models/lora_finetuned_ADDITIONAL_TUNING_deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    # # lora_weights_path = f"putnam-axiom/src/models/lora_finetuned_ADDITIONAL_TUNING_{base_model_name}"  # <-- Update this to your LoRA adapter directory.
    merged_model_dir = f"putnam-axiom/src/models/{base_model_name}"  # Directory to save the merged model.


    ensure_vocab_consistency(merged_model_dir)
    torch.cuda.empty_cache()
    gc.collect()
    
    model_list = [
        merged_model_dir
        # base_model_name
    ]

    final_scores = {}
    for model_name in model_list:
        print("=" * 100)
        print(f"running {model_name}")
        print("=" * 100)

        model = LLM(model_name,
                    tokenizer = model_name,
                    tensor_parallel_size = 4,
                    gpu_memory_utilization = 0.9,
                    # tokenizer = base_model_name,  # Use the tokenizer from the base model,
                    # max_model_len= 10000,  # Reduce below 69904 (KV cache limit)
                    # pipeline_parallel_size = 1,
                    trust_remote_code=True)
        lm_obj = MyLM(batch_size = 4,
                    model=model)
        task_manager = lm_eval.tasks.TaskManager()

        results = lm_eval.simple_evaluate(
            model=lm_obj,
            tasks=["putnam_axiom_variations"],
            task_manager=task_manager,
            write_out=False,
            random_seed = None,
            numpy_random_seed = None,
            torch_random_seed = None,
            fewshot_random_seed = None
        )
        
        print('=' * 50)
        print("results variation:", results["results"]["putnam_axiom_variations"].get("exact_match,none", None))
        var = results["results"]["putnam_axiom_variations"].get("exact_match,none", None)
        print('=' * 50)

        results = lm_eval.simple_evaluate(
            model=lm_obj,
            tasks=["putnam_axiom_variations_org"],
            task_manager=task_manager,
            write_out=False,
            random_seed = None,
            numpy_random_seed = None,
            torch_random_seed = None,
            fewshot_random_seed = None
        )
        
        print('=' * 50)
        print("results original:", results["results"]["putnam_axiom_variations_org"].get("exact_match,none", None))
        og = results["results"]["putnam_axiom_variations_org"].get("exact_match,none", None)
        print('=' * 50)

        final_scores[model_name] = [var, og]
        del model
        del lm_obj
        torch.cuda.empty_cache()
        gc.collect()

    print(final_scores)
    