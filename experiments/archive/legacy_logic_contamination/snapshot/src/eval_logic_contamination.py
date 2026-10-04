# using lm-harness/eval: https://chatgpt.com/c/67477267-a740-8001-894a-c5f22b24cc5f
from socket import gethostname
import os
import gc
import torch
from vllm import LLM, SamplingParams
from lm_eval import evaluator, tasks
from lm_eval.api.model import LM
import lm_eval.evaluator 
from os.path import expanduser
import fire
import wandb
from datetime import datetime
from typing import List, Tuple

_STOP_TOKENS: list[str] = ["Solution:", "Problem:", "Question:", "USER:", "USER:", "USER", "ASSISTANT:", "ASSISTANT", "Instruction:", "Instruction", "Response:", "Response"]
print(f'Original stop toks I had once: {len(_STOP_TOKENS)=} {_STOP_TOKENS=}')

#     raw_str_2_train_str = lambda examples : {'text': [f'problem: {prob}\n\nsolution: {sol}' for prob, sol in zip(examples['problem'], examples['solution'])]}
#     new, v2, no trian yet raw_str_2_train_str = lambda examples : {'text': [f'Problem:\n{prob}\n\nSolution:\n{sol}' for prob, sol in zip(examples['problem'], examples['solution'])]}
STOP_TOKENS: list[str] = ["problem:", "problem: ", "problem:\n", "Problem:", "Problem: ", "Problem:\n", "Question:", "USER:", "USER"]
print(f'New stop tokens: {len(STOP_TOKENS)=} {STOP_TOKENS=}')

class MyLM(LM):
    def __init__(self, model: LLM, batch_size: int = 16, model_name: str = 'model_name NOT SET.'):
        self.model = model
        super().__init__()
        self.batch_size = batch_size
        self.model_name = model_name

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
        print()
        # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
        # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop=STOP_TOKENS)
        # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=512, stop=STOP_TOKENS)
        params = SamplingParams(temperature=0, top_p=1, max_tokens=512, stop=STOP_TOKENS)
        prompts: List[str] = [request.args[0] for request in requests]
        outputs: list = self.model.generate(prompts, params)
        results: list[str] = [output.outputs[0].text for output in outputs]
        # print prompt result, what is going on during eval?
        assert len(prompts) == len(results), f'Fatal error: {wandb.run.alert(title="error during eval", text="len(prompts) != len(results)")}'
        for req_idx, (prompt, result) in enumerate(zip(prompts, results)):
            print(f'{"--"*20}\nProblem idx: {req_idx}. Model name: {self.model_name})')
            print(f'{"--"*20}\nInput Prompt Text:\n{prompt}\n')
            print(f'{"--"*20}\nGeneration:\n{result}\n')
        print()
        return results

def _generate_until(
        self, requests: List, 
        batch_size: int = 53, # idk why >53 fails but in sft it didnt? + auto:N is not working
        max_tokens: int = 512,
        # config: dict = {},
    ) -> List[str]:
    # Define sampling parameters
    params = SamplingParams(temperature=0, top_p=1, max_tokens=max_tokens, stop=STOP_TOKENS)

    # Extract prompts from requests
    prompts: List[str] = [request.args[0] for request in requests]

    # Prepare a container for all final results
    all_results: List[str] = []

    # Process prompts in batches
    for start_idx in range(0, len(prompts), batch_size):
        end_idx = start_idx + batch_size
        batch_prompts = prompts[start_idx:end_idx]

        # Generate outputs for this batch
        batch_outputs = self.model.generate(batch_prompts, params)
        batch_results = [output.outputs[0].text for output in batch_outputs]

        # Verification
        assert len(batch_prompts) == len(batch_results), (
            f"Fatal error: Number of prompts ({len(batch_prompts)}) does not match "
            f"number of results ({len(batch_results)})."
        )

        # Logging / debugging prints
        for req_idx, (prompt, result) in enumerate(zip(batch_prompts, batch_results), start=start_idx):
            print(f'{"--"*20}\nProblem idx: {req_idx}. Model name: {self.model_name})')
            print(f'{"--"*20}\nInput Prompt Text:\n{prompt}\n')
            print(f'{"--"*20}\nGeneration:\n{result}\n')

        # Extend the overall results
        all_results.extend(batch_results)
    return all_results

def do_lm_eval(model_name: str, task: str, kwargs: dict) -> dict: 
    gc.collect()
    torch.cuda.empty_cache()
    
    # model = LLM(model_name, trust_remote_code=True, gpu_memory_utilization=0.9, max_num_batched_tokens)
    model = LLM(model_name, trust_remote_code=True)
    lm_obj = MyLM(model=model, model_name=model_name)
    task_manager = tasks.TaskManager()
    results = lm_eval.evaluator.simple_evaluate(
        model=lm_obj,
        tasks=[task],
        batch_size="auto:6",
        task_manager=task_manager,
        write_out=False,
        limit=kwargs.get('limit', None), # limit the number of examples, if <1 then interpreted as %, default None --> all task benchmark
        random_seed=None,
        numpy_random_seed=None,
        torch_random_seed=None,
        fewshot_random_seed=None
    )

    del model
    del lm_obj
    gc.collect()
    torch.cuda.empty_cache()
    return results

def print_and_wandb_log_lm_eval_results(accuracy: float, checkpoint_idx: int, task: str, model_name: str, results: dict = {}) -> None:
    """ Log accuracy for each checkpoint """
    print('---')
    print(f'Checkpoint idx: {checkpoint_idx=}')
    print(f"Accuracy for that checkpoint: {accuracy=} ({checkpoint_idx=})")
    print(f"Checkpoint full name: {model_name=}")
    print('---')
    wandb.log({f"eval_bench/{task}/checkpoint_idx": checkpoint_idx, 
                f"eval_bench/{task}/accuracy": accuracy})


def main(**kwargs):
    gc.collect()
    torch.cuda.empty_cache()

    print(f'{"__"*32} Start of eval main: {main=}')
    print(f'{STOP_TOKENS=}')
    # task = kwargs.get('task', 'putnam_axiom_original')
    # task = kwargs.get('task', 'putnam_axiom_variations')
    task = kwargs.get('task', 'putnam_axiom_53')
    print(f'{task=}')
    # model_name_or_path = expanduser("~/data/runs_logic_cont/run_2024_m11_d20_t21h_22m_22s") # putnam-axiom 53 train 20 epochs
    # model_name_or_path = expanduser("~/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s") # putnam-axiom 53 train 100 epochs
    # model_name_or_path = expanduser("~/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s")
    # model_name_or_path = expanduser(kwargs.get('model_name_or_path', 'google/gemma-2-2b'))
    model_name_or_path = kwargs.get('model_name_or_path', "/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m12_d13_t23h_28m_52s")
    # model_name_or_path = kwargs.get('model_name_or_path', None)
    print(f'{model_name_or_path=}')
    # Extract and sort the model_list by checkpoint index
    model_list = sorted(
        [
            os.path.join(model_name_or_path, entry)
            for entry in os.listdir(model_name_or_path)
            if os.path.isdir(os.path.join(model_name_or_path, entry)) and entry.startswith("checkpoint-")
        ],
        key=lambda x: int(x.split('/')[-1].split('-')[-1])  # Extract the checkpoint index for sorting
    )
    print(f'{model_list}')
    print("\n".join(model_list))
    print(f'{len(model_list)=} (should be same as the expect steps/epochs +1 roughly)')
    # since we might be running multiple evals at once, the next time we run an eval we add it to the config, since wandb doesn't let you update the config if a key already has a value
    if task in wandb.config:
        next_task: list = wandb.config['task'].append(task)
        wandb.config.update({"model_list": model_list, 'task': next_task}, allow_val_change=True)
    else:
        wandb.config.update({"model_list": model_list, 'task': [task]}, allow_val_change=True)
    print(f'{wandb.config=}')
    # - Start eval run
    wandb.run.define_metric(f"{task}/eval_bench/accuracy", 
                            step_metric=f"{task}/eval_bench/checkpoint_idx")
    wandb.run.define_metric(f"{task}/eval_bench/checkpoint_idx") 
    model_2_accuracy = {model_name: None for model_name in model_list}
    print(f'{model_2_accuracy}')
    accs: list[float] = []
    for model_name in model_list:
        torch.cuda.empty_cache()
        gc.collect()

        print(f"{'=' * 100}")
        print(f'running model with name: {model_name}')
        print(f"{'=' * 100}")

        results: dict = do_lm_eval(model_name, task, kwargs)
        print(f"Arguments: {results['samples'][task][0]['arguments'][0][0]=}\nResponses: {results['samples'][task][0]['resps'][0][0]=}")
        print(f'Keys for Lm Eval: {results.keys()=}\nKeys for Lm Eval Task: {results["results"][task].keys()=}')

        # Log accuracy for each checkpoint
        accuracy: float = results["results"][task].get("exact_match,none", None) 
        model_2_accuracy[model_name] = accuracy
        accs.append(float(accuracy))
        checkpoint_idx = int(model_name.split('/')[-1].split('-')[-1])  # e.g., 'checkpoint-70'
        # do logging 
        print_and_wandb_log_lm_eval_results(accuracy, checkpoint_idx, task, model_name, results)

        gc.collect()
        torch.cuda.empty_cache()
    print(f'{model_2_accuracy=}\n{accs=}')
    print(f"{'=' * 100}")
    return {'model_2_accuracy': model_2_accuracy, 'accs': accs}

def _main(**kwargs):
    import wandb
    import os
    import time
    from datetime import datetime
    today = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss')
    run_name = f'{today}'
    run = wandb.init(
        mode=kwargs.get('mode', 'dryrun'), 
        # mode=kwargs.get('mode', 'online'), 
        project="putnam-axiom", 
        name=run_name, 
        save_code=True, 
        config=kwargs | {'hostname': gethostname()}
    )
    kwargs = kwargs | {'today': today}
    # os.environ['CUDA_VISIBLE_DEVICES'] = str(6) print("--> WARNING/REMINDER: cude device harcoded in script!\n"*10)
    print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', None)}")
    print(f'{run.get_url()=}')
    time.sleep(2)
    main(**kwargs)
    print(f'{run.get_url()=}')
    wandb.finish()

if __name__ == "__main__":
    import time
    start_time = time.time()
    fire.Fire(_main)
    elapsed_time = time.time() - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds, or {elapsed_time / 60:.2f} minutes, or {elapsed_time / 3600:.2f} hours.\a")
