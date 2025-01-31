import os
import gc
import torch
from lm_eval.api.model import LM
from lm_eval import evaluator, tasks
from openai import OpenAI
from typing import List, Tuple
import anthropic

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
                model = 'o1-preview',
                messages = [{"role": "user", "content": request.args[0]}],
                # max_tokens = 2048
            )
            results.append(response.choices[0].message.content)
            # response = client.messages.create(
            #     model = 'claude-3-5-sonnet-20241022',
            #     messages = [{"role": "user", "content": request.args[0]}],
            #     max_tokens = 2048
            # )
            # results.append(response.content[0].text)
        return results


torch.cuda.empty_cache()
gc.collect()

client = OpenAI(api_key = "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")
# client = anthropic.Anthropic(api_key = "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")

lm_obj = MyLM()
task_manager = tasks.TaskManager()
results = evaluator.simple_evaluate(
    model=lm_obj,
    tasks=["putnam_axiom_variations_org"],
    task_manager=task_manager,
    write_out=False,
    random_seed=None
)

print("results:", results["results"]["putnam_axiom_variations_org"].get("exact_match,none", None))