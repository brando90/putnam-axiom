import os
import gc
import torch
from lm_eval.api.model import LM
from lm_eval import evaluator, tasks
from openai import OpenAI
from typing import List, Tuple
import anthropic
import requests as req

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
    
    # def generate_until(self, requests: List) -> List[str]:
    #     results = []
    #     for request in requests:


    #         data = {
    #             "model": "deepseek-reasoner",  # Use 'deepseek-reasoner' for R1 model or 'deepseek-chat' for V3 model
    #             "messages": [
    #                 {"role": "user", "content": request.args[0]}
    #             ],
    #             "stream": False  # Disable streaming
    #         }

    #         response = req.post(url, headers=headers, json=data)

    #         if response.status_code == 200:
    #             result = response.json()
    #             results.append(result['choices'][0]['message']['content'])
    #         else:
    #             print("Error:", response.status_code)
    #         # response = client.chat.completions.create(
    #         #     model = 'deepseek-reasoner',
    #         #     messages = [{"role": "user", "content": request.args[0]}],
    #         #     # max_tokens = 2048
    #         # )
    #         # results.append(response.choices[0].message.content)
    #         # response = client.messages.create(
    #         #     model = 'claude-3-5-sonnet-20241022',
    #         #     messages = [{"role": "user", "content": request.args[0]}],
    #         #     max_tokens = 2048
    #         # )
    #         # results.append(response.content[0].text)
    #     return results
    def generate_until(self, requests: List) -> List[str]:
        results = []
        for request in requests:
            try:
                prompt = request.args[0]  # Ensure this works
                data = {
                    "model": "deepseek-reasoner",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }
                
                response = req.post(url, headers=headers, json=data, timeout=10)  # 10s timeout
                
                if response.status_code == 200:
                    result = response.json()
                    results.append(result['choices'][0]['message']['content'])
                else:
                    print(f"Error {response.status_code}: {response.text}")
                    results.append(f"Error: {response.status_code}")

            except Exception as e:
                print(f"Exception in generate_until: {e}")
                results.append("ERROR")


torch.cuda.empty_cache()
gc.collect()

# client = OpenAI(api_key = "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")
# client = OpenAI(api_key = "sk-83133dfe9dc64d4d8208d8f98f12686a", base_url = "https://api.deepseek.com")
API_KEY = "sk-83133dfe9dc64d4d8208d8f98f12686a"
url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}



# client = anthropic.Anthropic(api_key = "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")

lm_obj = MyLM()
task_manager = tasks.TaskManager()
results = evaluator.simple_evaluate(
    model=lm_obj,
    tasks=["putnam_axiom_variations"],
    task_manager=task_manager,
    write_out=False,
    random_seed=None
)

print("results variations:", results["results"]["putnam_axiom_variations"].get("exact_match,none", None))

results = evaluator.simple_evaluate(
    model=lm_obj,
    tasks=["putnam_axiom_variations_org"],
    task_manager=task_manager,
    write_out=False,
    random_seed=None
)

print("results original:", results["results"]["putnam_axiom_variations_org"].get("exact_match,none", None))