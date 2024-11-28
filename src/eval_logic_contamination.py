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

    def _generate_until(self, requests: List) -> List[str]:
        results = []
        context = []
        for request in requests:
            context = request.args[0]
            params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
            ret = self.model.generate(context, params)
            results.append(ret[0].outputs[0].text)
        return results

    def generate_until(self, requests: List) -> List[str]:
        # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
        print(f'{STOP_TOKENS=}')
        params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop=STOP_TOKENS)
        prompts: List[str] = [request.args[0] for request in requests]
        outputs: list = self.model.generate(prompts, params)
        results: list[str] = [output.outputs[0].text for output in outputs]
        return results

def main(**kwargs):
    # task = kwargs.get('task', 'putnam_axiom_original')
    task = kwargs.get('task', 'putnam_axiom_variations')
    # task = kwargs.get('task', 'putnam_axiom_53')
    print(f'{task=}')
    directory_path = expanduser("~/data/runs_logic_cont/run_2024_m11_d20_t21h_22m_22s") # putnam-axiom 53 train 20 epochs
    directory_path = expanduser("~/data/runs_logic_cont/run_2024_m11_d23_t21h_55m_07s") # putnam-axiom 53 train 100 epochs
    directory_path = expanduser(kwargs.get('model_name_or_path', 'google/gemma-2-2b'))
    print(f'{directory_path=}')
    # Extract and sort the model_list by checkpoint index
    model_list = sorted(
        [
            os.path.join(directory_path, entry)
            for entry in os.listdir(directory_path)
            if os.path.isdir(os.path.join(directory_path, entry)) and entry.startswith("checkpoint-")
        ],
        key=lambda x: int(x.split('/')[-1].split('-')[-1])  # Extract the checkpoint index for sorting
    )
    print(f'{model_list=}')
    # since we might be running multiple evals at once, the next time we run an eval we add it to the config, since wandb doesn't let you update the config if a key already has a value
    if task in wandb.config:
        next_task: list = wandb.config['task'].append(task)
        wandb.config.update({"model_list": model_list, 'task': next_task}, allow_val_change=True)
    else:
        wandb.config.update({"model_list": model_list, 'task': [task]}, allow_val_change=True)
    print(f'{wandb.config=}')
    
    print(model_list[:3])
    folder_count = sum(os.path.isdir(os.path.join(directory_path, entry)) for entry in os.listdir(directory_path))
    print(f"Total number of folders (non-recursive) in the directory: {folder_count}")

    torch.cuda.empty_cache()
    gc.collect()

    print(f'{model_list=}')
    wandb.run.define_metric(f"{task}/eval_bench/accuracy", 
                            step_metric=f"{task}/eval_bench/checkpoint_idx")
    wandb.run.define_metric(f"{task}/eval_bench/checkpoint_idx") 
    model_2_accuracy = {model_name: None for model_name in model_list}
    accs: list[float] = []
    for model_name in model_list:
        print(f"{'=' * 100}running {model_name} {task=}{'=' * 100}")

        model = LLM(model_name, trust_remote_code=True)
        lm_obj = MyLM(model=model)
        task_manager = tasks.TaskManager()

        results = lm_eval.evaluator.simple_evaluate(
            model=lm_obj,
            tasks=[task],
            task_manager=task_manager,
            write_out=False,
            random_seed=None,
            numpy_random_seed=None,
            torch_random_seed=None,
            fewshot_random_seed=None
        )
        print(f"arguments: {results['samples'][task][0]['arguments'][0][0]=}")
        print(f"resps: {results['samples'][task][0]['resps'][0][0]=}")
        print(f'{results.keys()=}')
        print(f'{results["results"][task].keys()=}')

        print("results:", results["results"][task].get("exact_match,none", None))
        accuracy = results["results"][task].get("exact_match,none", None) 
        model_2_accuracy[model_name] = accuracy
        accs.append(float(accuracy))
        checkpoint_idx = int(model_name.split('/')[-1].split('-')[-1])  # e.g., 'checkpoint-70'
        print(f"{accuracy=} for model ckpt idk: {checkpoint_idx=}")
        
        # Log accuracy for each checkpoint
        wandb.log({f"{task}/eval_bench/checkpoint_idx": checkpoint_idx, 
                   f"{task}/eval_bench/accuracy": accuracy})

        del model
        del lm_obj
        torch.cuda.empty_cache()
        gc.collect()
    print(f'{model_2_accuracy=}\n{accs=}')
    print(f"{'=' * 100}")
    return {'model_2_accuracy': model_2_accuracy, 'accs': accs}

def _main(**kwargs):
    today = datetime.now().strftime('%Y_m%m_d%d_t%Hh_%Mm_%Ss')
    run_name = f'{today}'
    run = wandb.init(
        mode=kwargs.get('mode', 'dryrun'), 
        project="putnam-axiom", 
        name=run_name, 
        save_code=True, 
        config=kwargs | {'hostname': gethostname()}
    )
    kwargs = kwargs | {'today': today}
    main(**kwargs)
    print(f'{run.get_url()=}')
    wandb.finish()

if __name__ == "__main__":
    import time
    start_time = time.time()
    fire.Fire(_main)
    elapsed_time = time.time() - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds, or {elapsed_time / 60:.2f} minutes, or {elapsed_time / 3600:.2f} hours.\a")