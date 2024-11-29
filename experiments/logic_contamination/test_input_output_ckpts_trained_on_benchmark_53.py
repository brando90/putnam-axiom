# want to see what the models trained on eval set are outputting, why isn't the acc 100% for very overtrained models?
from vllm import LLM, SamplingParams

STOP_TOKENS: list[str] = ["problem:", "problem: ", "problem:\n", "Problem:", "Problem: ", "Problem:\n", "Question:", "USER:", "USER"]
print(f'New stop tokens: {len(STOP_TOKENS)=} {STOP_TOKENS=}')

def generate_until(model: LLM, requests: list) -> list[str]:
    # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
    params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop=STOP_TOKENS)
    # prompts: list[str] = [request.args[0] for request in requests]
    prompts: list[str] = [request for request in requests]
    outputs: list = model.generate(prompts, params)
    results: list[str] = [output.outputs[0].text for output in outputs]
    return results

# model = "facebook/opt-125m"
# model = "google/gemma-2-2b"
# model = "meta-llama/Llama-3.1-8B"
model = "/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m11_d27_t19h_20m_06s/checkpoint-148"
model = LLM(model=model)

requests = ['Hello']
requests = ['Evaluate $\\int_0^\\infty t^{-1/2}e^{-1985(t+t^{-1})}\\,dt$. ']

raw_str_2_train_str = lambda examples : {'text': [f'Problem:\n{prob}\n\nSolution:\n{sol}' for prob, sol in zip(examples['problem'], examples['solution'])]}
raw_str_2_train_str = lambda prob, sol: f'Problem:\n{prob}\n\nSolution:\n{sol}'

problem = "Evaluate $\\int_0^\\infty t^{-1/2}e^{-1985(t+t^{-1})}\\,dt$. You may assume that $\\int_{-\\infty}^\\infty e^{-x^2}\\,dx = \\sqrt{\\pi}$."
raw_str_2_train_str = lambda prob: f'Problem:\n{prob}\n\n'
requests = [raw_str_2_train_str(problem)]

# - Run it
print(f'{requests=}')
results = generate_until(model, requests)

print(f'{results=}')
print()