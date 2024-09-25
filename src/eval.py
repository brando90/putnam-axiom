
import argparse
import gc
import os
import subprocess
from pathlib import Path
import json
import pandas as pd
import torch
from prompts import generate_prompt
from util import *
from vllm import LLM, SamplingParams

def main(
    data_dir: str = '~/putnam-math/data/Putnam_MATH_original_static_final',
    prompt_name: str = "general_few_shot_prompt",
    model_name: str = 'mistralai/Mistral-7B-v0.1',
    output_dir: str = 'putnam-math/py_src/evals/modelOutputs',
    temperature: float = 0.9,
    top_p: float = 0.95,
    max_tokens: float = 2048,
    stop: str = 'Problem:\n',
    repeat_eval: int = 5,
    verbose: bool = True
):
    data_dir: Path = Path(data_dir).expanduser()
    problems = generate_problems(data_dir)
    prompt = generate_prompt(prompt_name, problems)
    CUDA_VISIBLE_DEVICES = get_gpu_with_most_free_memory()
    os.environ['CUDA_VISIBLE_DEVICES'] = get_gpu_with_most_free_memory()
    print(CUDA_VISIBLE_DEVICES)
    if not CUDA_VISIBLE_DEVICES:
        raise Exception("No devices available")
    
    print(len(problems))

    # model = LLM(model_name, trust_remote_code=True)
    # params = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens, stop=stop)

    # for i in range(repeat_eval):
    #     outputs = model.generate(prompt, params)
    #     results = [o.outputs[0].text for o in outputs]
    #     acc, correct, predicted_answers = compute_accuracy(results, problems, verbose)
    #     save_csv(output_dir, model_name, prompt_name, predicted_answers, problems, results)
    #     del model
    #     torch.cuda.empty_cache()
    #     gc.collect()

def get_gpu_with_most_free_memory():
    result = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.free,index', '--format=csv,nounits,noheader'], 
        encoding='utf-8'
    )
    free_memory = [line.split(',') for line in result.strip().split('\n')]
    best_gpu = max(free_memory, key=lambda x: int(x[0]))[1]
    return best_gpu

def generate_problems(prob_file):
    problems = []
    with open(prob_file, 'r') as f:
        dataset = json.load(f)
    for entry in dataset:
        assert 'id' in entry
        assert 'problem' in entry
        assert 'solution' in entry
        try:
            entry['answer'] = ground_truth_boxed_answer(entry['solution'])
        except:
            print('No boxed answer found for problem ', entry['id'])
            continue
        
        problems.append(entry)
    
    return problems

def compute_accuracy(results, problems, verbose):
    predicted_answers = []
    for r in results:
        try:
            predicted_answers.append(ground_truth_boxed_answer(r))
        except:
            predicted_answers.append(get_generated_answer(r))

    assert len(predicted_answers) == len(problems)
    correct = []
    sum = 0

    for p, a in zip(predicted_answers, problems):

        simp_p = simplify_answer(p)
        simp_a = simplify_answer(a['answer'])
        if (simp_p == simp_a):
            sum += 1
            correct.append(a['id'])

    acc = sum / len(predicted_answers)
    if(verbose):
        print(acc)
        print(correct)
    return acc, correct, predicted_answers

def save_csv(dir, model_name, prompt_type, predicted_answers, problems, results):
    model_name = model_name.replace("/", "-")

    problem_ids = [p['id'] for p in problems]
    problem_answers = [p['answer'] for p in problems]
    correct_problems = [p == a for p,a in zip(predicted_answers,problem_answers)]
    final_data = pd.DataFrame({'Problem ID:' : problem_ids, 'Predicted Solution': results, 'Correct': correct_problems})

    final_data.to_csv(f'{dir}/{model_name}_{prompt_type}_outputs.csv')

if __name__ == '__main__':
    torch.cuda.empty_cache()
    gc.collect()
    
    parser = argparse.ArgumentParser(description="Run model evaluation with specified parameters")

    parser.add_argument('--data_dir', type=str, default='putnam-axiom/data/Putnam_AXIOM_Original.json', help="Directory containing the data")
    parser.add_argument('--prompt_name', type=str, default="general_few_shot_prompt", help="Name of the prompt to use")
    parser.add_argument('--model_name', type=str, default='mistralai/Mistral-7B-v0.1', help="Name of the model to use")
    parser.add_argument('--output_dir', type=str, default='putnam-axiom/data/LM_Outputs', help="Directory to save the output")
    parser.add_argument('--temperature', type=float, default=0.9, help="Temperature setting for model generation")
    parser.add_argument('--top_p', type=float, default=0.95, help="Top-p setting for model generation")
    parser.add_argument('--max_tokens', type=int, default=2048, help="Maximum number of tokens for model generation")
    parser.add_argument('--stop', type=str, default='Problem:\n', help="Stop sequence for the model generation")
    parser.add_argument('--repeat_eval', type=int, default=5, help="Number of times to repeat the evaluation")
    parser.add_argument('--verbose', type=bool, default=True, help="Whether to print verbose output")

    args = parser.parse_args()

    main(
        data_dir=args.data_dir,
        prompt_name=args.prompt_name,
        model_name=args.model_name,
        output_dir=args.output_dir,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        stop=args.stop,
        repeat_eval=args.repeat_eval,
        verbose=args.verbose
    )

    