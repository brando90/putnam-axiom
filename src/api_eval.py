import os
import gc
import torch
import re
from lm_eval.api.model import LM
from lm_eval import evaluator, tasks
from openai import OpenAI
from typing import List, Tuple
import anthropic
import requests as req
import json

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
        group_size = 10  # Process 10 requests per API call

        with open("putnam-axiom/data/Putnam-AXIOM_Variations_v4/original.json", "r") as f:
            originals = json.load(f)
        
        # Group the requests into chunks of group_size
        for i in range(0, len(requests), group_size):
            group = requests[i:i+group_size]
            group_originals = originals[i:i+group_size]
            # Build the combined prompt
            prompt = (
                "You are a math expert. You will be given a problem and its solution. Your task is to solve the problem and provide the solution in a boxed format.\n"
                "Here are many examples which will be very similar to the problems you will be given:\n\n"
            )
            # Append each original problem/solution pair as in-context examples.
            for item in group_originals:
                prompt += f"Problem: {item['problem']}\nSolution: {item['solution']}\n\n"
            prompt += "Now, solve the following problems:\n\n"
            # Append each variation problem.
            for idx, req_item in enumerate(group):
                data = req_item.args[0]  # expecting key 'variation_problem'
                spec_prompt = prompt + data
                try:
                    # data_payload = {
                    #     "model": "gpt-4o",  # Use 'deepseek-reasoner' (or change to 'deepseek-chat' for V3)
                    #     "messages": [{"role": "user", "content": prompt}],
                    #     "stream": False
                    # }
                    # response = req.post(url, headers=headers, json=data_payload, timeout=10)
                    response = client.chat.completions.create(
                        model='gpt-4o',
                        messages=[{"role": "user", "content": spec_prompt}],
                        max_tokens=2048
                    )
                    result = response.choices[0].message.content
                    results.append(result)
                    # if response.status_code == 200:
                    #     result = response.json()
                    #     answer_text = result['choices'][0]['message']['content']
                    #     # Extract all the boxed answers from the response text.
                    #     boxed_answers = re.findall(r'\\boxed\{([^}]+)\}', answer_text)
                        
                    #     if len(boxed_answers) != len(group):
                    #         print(f"Warning: expected {len(group)} answers but found {len(boxed_answers)}.\nRaw answer: {answer_text}")
                        
                    #     results.extend(boxed_answers)
                    # else:
                    #     print(f"Error {response.status_code}: {response.text}")
                    #     results.extend(["Error: " + str(response.status_code)] * len(group))
                
                except Exception as e:
                    print(f"Exception in generate_until for group starting at index {i}: {e}")
                    results.extend(["ERROR"] * len(group))
        
        return results
    # def generate_until(self, requests: List) -> List[str]:
    #     results = []
    #     for request in requests:
    #         try:
    #             prompt = request.args[0]  # Ensure this works
    #             data = {
    #                 "model": "deepseek-reasoner",
    #                 "messages": [{"role": "user", "content": prompt}],
    #                 "stream": False
    #             }
                
    #             response = req.post(url, headers=headers, json=data, timeout=10)  # 10s timeout
                
    #             if response.status_code == 200:
    #                 result = response.json()
    #                 results.append(result['choices'][0]['message']['content'])
    #             else:
    #                 print(f"Error {response.status_code}: {response.text}")
    #                 results.append(f"Error: {response.status_code}")

    #         except Exception as e:
    #             print(f"Exception in generate_until: {e}")
    #             results.append("ERROR")


torch.cuda.empty_cache()
gc.collect()

client = OpenAI(api_key = "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")
# client = OpenAI(api_key = "sk-83133dfe9dc64d4d8208d8f98f12686a", base_url = "https://api.deepseek.com")




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
print('*' * 20)
print("results variations:", results["results"]["putnam_axiom_variations"].get("exact_match,none", None))
print('*' * 20)
results = evaluator.simple_evaluate(
    model=lm_obj,
    tasks=["putnam_axiom_variations_org"],
    task_manager=task_manager,
    write_out=False,
    random_seed=None
)
print('*' * 20)
print("results original:", results["results"]["putnam_axiom_variations_org"].get("exact_match,none", None))
print('*' * 20)