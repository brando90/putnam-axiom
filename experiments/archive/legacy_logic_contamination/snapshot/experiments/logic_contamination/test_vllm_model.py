# want to see what the models trained on eval set are outputting, why isn't the acc 100% for very overtrained models?
from vllm import LLM, SamplingParams

STOP_TOKENS: list[str] = ["problem:", "problem: ", "problem:\n", "Problem:", "Problem: ", "Problem:\n", "Question:", "USER:", "USER"]
print(f'New stop tokens: {len(STOP_TOKENS)=} {STOP_TOKENS=}')


def generate_until(model: LLM, requests: list) -> list[str]:
    # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
    print(f'{STOP_TOKENS=}')
    params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop=STOP_TOKENS)
    # prompts: list[str] = [request.args[0] for request in requests]
    prompts: list[str] = [request for request in requests]
    outputs: list = model.generate(prompts, params)
    results: list[str] = [output.outputs[0].text for output in outputs]
    return results

requests = ['Hello', 'Hi']
model = "facebook/opt-125m"
model = "google/gemma-2-2b"
model = "meta-llama/Llama-3.1-8B"
model = LLM(model=model)

results = generate_until(model, requests)

print(f'{results=}')
print()