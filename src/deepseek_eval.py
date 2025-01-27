import os
import gc
import torch
from lm_eval.api.model import LM
from lm_eval import evaluator, tasks
from openai import OpenAI
from typing import List, Tuple

################################################################
#  Custom LM for Deepseek R1
################################################################
class DeepseekR1LM(LM):
    """
    A custom LM class that queries Deepseek’s API for
    both generation and (optionally) log-likelihood.
    """
    def __init__(self, model_name: str = "deepseek-r1", batch_size=1):
        super().__init__()
        self.model_name = model_name
        self.batch_size = batch_size

    def loglikelihood(self, requests: List) -> List[Tuple[float, bool]]:
        # If the Deepseek API does NOT provide log-likelihood endpoints,
        # you have two options:
        #   1) Return dummy values or skip tasks that need loglikelihood.
        #   2) Approximate log-probs by manually doing trick with "logit_bias"
        #      if the API supports it (often not possible in ChatCompletion).
        # For now, let's just return dummy:
        return [(0.0, True) for _ in requests]

    def loglikelihood_rolling(self, requests: List) -> List[float]:
        # Same situation as above
        return [0.0 for _ in requests]

    def generate_until(self, requests: List) -> List[str]:
        # This calls the chat completions endpoint with your model.
        
        results = []
        for request in requests:
            # response = client.chat.completions.create(
            #     model = 'DeepSeek-R1',
            #     messages = [{"role": "user", "content": request.args[0]}],
            #     max_tokens = 2048
            # )
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "user", "content": request.args[0]}
                ],
                stream=False
            )
            results.append(response.choices[0].message.content)
        
        # outputs = []
        # for req in requests:
        #     prompt = req.args[0]
            # response = client.ChatCompletion.create(
            #     model=self.model_name,   # "deepseek-r1" or "gpt-4o" if that’s correct
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=2048,
            #     temperature=0.9,
            #     top_p=0.95
            # )
            # outputs.append(response.choices[0].message.content)
        print("results", results)
        return results


################################################################
#  If you want to handle other models in the same file:
################################################################
from vllm import LLM as VLLMModel

class VLLMLM(LM):
    """
    A custom LM class that wraps vllm’s LLM object for loglikelihood and generation.
    """
    def __init__(self, hf_model_name: str, batch_size: int = 16):
        super().__init__()
        self.batch_size = batch_size
        self.model = VLLMModel(hf_model_name, trust_remote_code=True)
        # If you need a tokenizer or additional logic, do that here.

    def loglikelihood(self, requests: List) -> List[Tuple[float, bool]]:
        # You will have to implement or approximate log-likelihood
        # with vllm (or skip tasks that need log-likelihood).
        pass

    def loglikelihood_rolling(self, requests: List) -> List[float]:
        pass

    def generate_until(self, requests: List) -> List[str]:
        # Example usage with vllm:
        #   from vllm import SamplingParams
        #   sampling_params = SamplingParams(max_tokens=128, ...)
        #   results = self.model.generate([req.args[0] for req in requests], sampling_params)
        # You’d then parse those results and return a list of strings.
        pass


################################################################
#  Main code
################################################################
torch.cuda.empty_cache()
gc.collect()

model_list = [
    "deepseek-ai/DeepSeek-R1",
    # Add other HF models if you wish:
    # "bigscience/bloom-560m",
    # "decapoda-research/llama-7b-hf",
    # etc.
]

client = OpenAI(api_key = "sk-83133dfe9dc64d4d8208d8f98f12686a", base_url = "https://api.deepseek.com")

for model_name in model_list:
    if "deepseek" in model_name.lower():
        print(f"Using DeepseekR1LM for {model_name}")
        lm_obj = DeepseekR1LM(model_name="DeepSeek-R1")  # or "DeepSeek-R1" if that’s the correct name
    else:
        print(f"Using vllm for {model_name}")
        lm_obj = VLLMLM(model_name)

    # Evaluate with LM-Eval
    task_manager = tasks.TaskManager()
    results = evaluator.simple_evaluate(
        model=lm_obj,
        tasks=["putnam_axiom_original"],
        task_manager=task_manager,
        write_out=False,
        random_seed=None
    )

    print("RESULTS:", results)