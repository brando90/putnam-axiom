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
        for request in requests:
            context.append(request.args[0])
        
        params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
        results = self.model.generate(context, params)
        # for request in requests:
        #     response = client.chat.completions.create(
        #         model = 'gpt-4o',
        #         messages = [{"role": "user", "content": request.args[0]}],
        #         max_tokens = 2048
        #     )
        #     results.append(response.choices[0].message.content)
        return results

model_list = [
            # 'mistralai/Codestral-22B-v0.1'
            # 'meta-llama/Llama-3.1-70B'
            # "meta-llama/Meta-Llama-3.1-8B", 
            #  "meta-llama/Meta-Llama-3.1-8B-Instruct", 
            #   "mistralai/Mistral-7B-v0.1", 
            #   "mistralai/Mistral-7B-Instruct-v0.1",
            #   "google/gemma-7b",
            # "deepseek-ai/DeepSeek-R1"
            #   "google/gemma-2b",
            #   "google/gemma-7b-it",
            #   "google/gemma-2b-it",
            #   "deepseek-ai/deepseek-math-7b-base",
            #   "deepseek-ai/deepseek-math-7b-rl",
            #   "deepseek-ai/deepseek-math-7b-instruct",
            #   "AI-MO/NuminaMath-7B-TIR",
            #   "Qwen/Qwen2-Math-7B",
            #   "Qwen/Qwen2-Math-7B-Instruct"
]

# os.environ["CUDA_VISIBLE_DEVICES"] = 0,2,3,4
torch.cuda.empty_cache()
gc.collect()

for model_name in model_list:
    print("=" * 100)
    print(f"running {model_name}")
    print("=" * 100)

    model = LLM(model_name, 
                # tensor_parallel_size = 2,
                # pipeline_parallel_size = 1,
                trust_remote_code=True)
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
print("results:", results["results"]["putnam_axiom_original"].get("exact_match,none", None))

# for model_name in model_list:
#     print("=" * 100)
#     print(f"running {model_name}")
#     print("=" * 100)

#     model = LLM(model_name, 
#                 # tensor_parallel_size = 4,
#                 trust_remote_code=True,
#                 # gpu_memory_utilization=0.9,
#                 # max_model_len=8192
#                 )
#     lm_obj = MyLM(model=model)
#     task_manager = lm_eval.tasks.TaskManager()

#     results = lm_eval.simple_evaluate(
#         model=lm_obj,
#         tasks=["putnam_axiom_original"],
#         task_manager=task_manager,
#         write_out=False,
#         random_seed = None,
#         numpy_random_seed = None,
#         torch_random_seed = None,
#         fewshot_random_seed = None
#     )

#     print("results:", results["results"]["putnam_axiom_original"].get("exact_match,none", None))

#     del model
#     del lm_obj
#     torch.cuda.empty_cache()
#     gc.collect()





# import os
# from huggingface_hub import login
# import gc
# from vllm import LLM, SamplingParams
# import lm_eval
# from lm_eval import evaluator, tasks, api
# from lm_eval.api.model import LM

# from typing import List, Tuple
# import torch
# import random
# import json
# from openai import OpenAI
# import anthropic

# class MyLM(LM):
#     def __init__(self, model, batch_size: int = 16):
#         self.model = model
#         super().__init__()
#         self.batch_size = batch_size

#     def loglikelihood(self, requests: List) -> List[Tuple[float, bool]]:
#         results = []
#         for request in requests:
#             context, continuation = request.args()
#             # Replace this with actual log-likelihood computation using your model
#             logprob = self.model.compute_loglikelihood(context, continuation)
#             isgreedy = self.model.is_greedy(context, continuation)
#             results.append((logprob, isgreedy))
#         return results

#     def loglikelihood_rolling(self, requests: List) -> List[float]:
#         results = []
#         for request in requests:
#             context, = request.args()
#             logprob = self.model.compute_rolling_loglikelihood(context)
#             results.append(logprob)
#         return results
    
#     def generate_until(self, requests: List) -> List[str]:
#         results = []
#         context = []
#         for request in requests:
#             context.append(request.args[0])

#         params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
#         generated = self.model.generate(context, params)
#         # if generation_result and generation_result[0].outputs:
#         #     results.append(generation_result[0].outputs[0].text)
#         # else:
#         #     results.append("")  # Append an empty string if no valid output
#         for output in generated:
#             if hasattr(output, "text"):  # Check if 'text' attribute exists
#                 results.append(output.text)
#             else:
#                 results.append(str(output))  # Fallback to string conversion
#         return results

# # os.environ["CUDA_VISIBLE_DEVICES"] = "1"
# torch.cuda.empty_cache()
# gc.collect()

# model_list = [
#             # "meta-llama/Meta-Llama-3-8B", ### DOESNT WORK???
#             # "meta-llama/Meta-Llama-3-8B-Instruct", 
#             # "mistralai/Mistral-7B-v0.3",  ### 5
#             # "mistralai/Mistral-7B-Instruct-v0.3",
#             # "google/gemma-7b", ### 6 TERMINAL: eval_google
#             # "google/gemma-2b",
#             # "google/gemma-7b-it",
#             # "google/gemma-2b-it",
#             # "deepseek-ai/deepseek-math-7b-base", ### 7 TERMINAL: eval_deepseek
#             # "deepseek-ai/deepseek-math-7b-rl", # GPU 0
#             # "deepseek-ai/deepseek-math-7b-instruct",
#             # "AI-MO/NuminaMath-7B-TIR", ### 3
#             # "Qwen/Qwen2-Math-7B", ### 4
#             # "Qwen/Qwen2-Math-7B-Instruct",
#             "meta-llama/Meta-Llama-3.1-70B"
#             ]

# # for running multiple models or 
# final = {}
# gpu_ids = [4,6,7]
# for model_name in model_list:
#     print("=" * 100)
#     print(f"running {model_name}")
#     print("=" * 100)
#     folder_name = f'putnam-axiom/src/model_evals/test/{os.path.basename(model_name)}'
#     os.makedirs(folder_name, exist_ok = True)

#     model = LLM(model_name, 
#                 tensor_parallel_size = 4,
#                 # pipeline_parallel_size = 2,
#                 trust_remote_code=True)
#     lm_obj = MyLM(model=model)
#     task_manager = lm_eval.tasks.TaskManager()
#     for i in range(5):
#         print("=" * 100)
#         print(f"run number {i}")
#         print("=" * 100)

#         results = lm_eval.simple_evaluate(
#             model=lm_obj,
#             tasks=["putnam_axiom_original"],
#             task_manager=task_manager,
#             write_out=False,
#             random_seed = None,
#             numpy_random_seed = None,
#             torch_random_seed = None,
#             fewshot_random_seed = None
#         )
#         with open (f'{folder_name}/run{i}.json', 'w') as outfile:
#             json.dump(results, outfile, indent = 6)
#         # print("results:", results["results"]["axiom_variations"].get("exact_match,none", None))
#         # final[model_name] = results["results"]["axiom_variations"].get("exact_match,none", None)
        
#     del model
#     del lm_obj
#     torch.cuda.empty_cache()
#     gc.collect()