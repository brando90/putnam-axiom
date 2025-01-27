import os
import gc
import torch
from lm_eval.api.model import LM
from lm_eval import evaluator, tasks
from openai import OpenAI
from typing import List, Tuple

class MyLM(LM):
    def __init__(self, batch_size: int = 16):
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

client = OpenAI(api_key = "")

lm_obj = MyLM()
task_manager = tasks.TaskManager()
results = evaluator.simple_evaluate(
    model=lm_obj,
    tasks=["putnam_axiom_original"],
    task_manager=task_manager,
    write_out=False,
    random_seed=None
)

print("results:", results["results"]["putnam_axiom_original"].get("exact_match,none", None))