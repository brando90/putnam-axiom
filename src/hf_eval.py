"""
File to evaluate Deepseek R1 and other models that are not compatible with VLLM.

"""

import os
from huggingface_hub import login
import gc
from vllm import LLM, SamplingParams
import lm_eval
from lm_eval import evaluator, tasks, api
from lm_eval.api.model import LM
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel

from typing import List, Tuple
import torch
import random
import json
from openai import OpenAI
import anthropic


class MyLM(LM):
    def __init__(self, model = None, batch_size: int = 16):
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
        # for request in requests:
        #     context.append(request.args[0])
        
        # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
        # results = self.model.generate(context, params)
        for request in requests:
            response = client.chat.completions.create(
                model = 'gpt-4o',
                messages = [{"role": "user", "content": request.args[0]}],
                max_tokens = 2048
            )
            results.append(response.choices[0].message.content)
        return results
torch.cuda.empty_cache()
gc.collect()

model_list = [
    "deepseek-ai/DeepSeek-R1"
]

API_KEY = API_KEY = "sk-83133dfe9dc64d4d8208d8f98f12686a"
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

for model_name in model_list:
    # Load the model using Hugginface 
    # model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
    # tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = LLM(model_name, trust_remote_code= True)
    lm_obj = MyLM(model=model)
    task_manager = lm_eval.tasks.TaskManager()

    results = lm_eval.simple_evaluate(
        model=lm_obj,
        tasks=["putnam_axiom_original"],
        task_manager=task_manager,
        write_out=False,
        random_seed = None,
        numpy_random_seed = None,
        torch_random_seed = None,
        fewshot_random_seed = None
    )
