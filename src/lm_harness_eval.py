import os
from huggingface_hub import login
import gc
from vllm import LLM, SamplingParams
import lm_eval
from lm_eval import evaluator, tasks, api
from lm_eval.api.model import LM

from typing import List, Tuple
import torch
import random
import json
from openai import OpenAI
import anthropic

class MyLM(LM):
    def __init__(self, model, batch_size: int = 16):
        self.model = model
        super().__init__()
        self.batch_size = batch_size

    def loglikelihood(self, requests: List) -> List[Tuple[float, bool]]:
        results = []
        for request in requests:
            context, continuation = request.args()
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

        if self.model.split('-')[0] == "GPT":
            model_name = self.model.split("-")[1:]
            for request in requests:
                response = client.chat.completions.create(
                    model = model_name,
                    messages = [{"role": "user", "content": request.arguments[0]}],
                    max_tokens = 2048
                )
                results.append(response.choices[0].message.content)

        elif self.model.split('-')[0] == "claude":
            for request in requests:
                message = client.messages.create(
                    model= self.model,
                    max_tokens=2048,
                    temperature=0.9,
                    messages=[{"role": "user", "content": request.arguments[0]}]
                )
                results.append(message.content[0].text)
        else:
            for request in requests:
                context.append(request.args[0])
            
            params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
            results = self.model.generate(context, params)
            results = results[0].outputs[0].text

        return results

os.environ["CUDA_VISIBLE_DEVICES"] = "3"
torch.cuda.empty_cache()
gc.collect()

model = LLM('model_name', trust_remote_code=True)
lm_obj = MyLM()
task_manager = lm_eval.tasks.TaskManager()

results = lm_eval.simple_evaluate(
    model=lm_obj,
    tasks=["axiom"],
    task_manager=task_manager,
    write_out=False,
)

print("results:", results["results"]["axiom"].get("exact_match,none", None))


# for running multiple models or 
final = {}
for model_name in model_list:
    print("=" * 100)
    print(f"running {model_name}")
    print("=" * 100)

    model = LLM(model_name, trust_remote_code=True)
    lm_obj = MyLM(model=model)
    task_manager = lm_eval.tasks.TaskManager()

    for i in range(5):

        print("=" * 100)
        print(f"run number {i}")
        print("=" * 100)

        results = lm_eval.simple_evaluate(
            model=lm_obj,
            tasks=["axiom_variations"],
            task_manager=task_manager,
            write_out=False,
            random_seed = None,
            numpy_random_seed = None,
            torch_random_seed = None,
            fewshot_random_seed = None
        )

        print("results:", results["results"]["axiom_variations"].get("exact_match,none", None))
        final[model_name] = results["results"]["axiom_variations"].get("exact_match,none", None)

    del model
    del lm_obj
    torch.cuda.empty_cache()
    gc.collect()

    print("=" * 100)
    print(final)
    print("=" * 100)