# want to see what the models trained on eval set are outputting, why isn't the acc 100% for very overtrained models?
import os
import time
start_time = time.time()
from vllm import LLM, SamplingParams

STOP_TOKENS: list[str] = ["problem:", "problem: ", "problem:\n", "Problem:", "Problem: ", "Problem:\n", "Question:", "USER:", "USER"]
print(f'New stop tokens: {len(STOP_TOKENS)=} {STOP_TOKENS=}')

def generate_until(model: LLM, requests: list) -> list[str]:
    # params = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=2048, stop='Problem:\n')
    # params = SamplingParams(temperature=0, top_p=1, max_tokens=512, stop=STOP_TOKENS, ignore_eos=True)
    params = SamplingParams(temperature=0, top_p=1, max_tokens=512, stop=STOP_TOKENS, skip_special_tokens=False)
    # prompts: list[str] = [request.args[0] for request in requests]
    prompts: list[str] = [request for request in requests]
    outputs: list = model.generate(prompts, params)
    results: list[str] = [output.outputs[0].text for output in outputs]
    return results

"""
python $HOME/putnam-axiom/experiments/logic_contamination/test_input_output_ckpts_trained_on_benchmark_53.py
"""
os.environ['CUDA_VISIBLE_DEVICES'] = str(3)

# model = "facebook/opt-125m"
#
model = "meta-llama/Llama-3.1-8B"
model = "/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m11_d27_t19h_20m_06s/checkpoint-148"
# model = "/lfs/skampere1/0/brando9/data/runs_logic_cont/run_2024_m11_d27_t19h_20m_06s/checkpoint-121"
#
# model = "google/gemma-2-2b"
# ins & 9b
print(f'{model=}')
model = LLM(model=model)

raw_str_2_train_str = lambda examples : {'text': [f'Problem:\n{prob}\n\nSolution:\n{sol}' for prob, sol in zip(examples['problem'], examples['solution'])]}
raw_str_2_train_str = lambda prob, sol: f'Problem:\n{prob}\n\nSolution:\n{sol}'

problem = "Evaluate $\\int_0^\\infty t^{-1/2}e^{-1985(t+t^{-1})}\\,dt$. You may assume that $\\int_{-\\infty}^\\infty e^{-x^2}\\,dx = \\sqrt{\\pi}$."
solution = "Let $I(x) = \\int_0^\\infty t^{-1/2}e^{-at-x/t}\\, dt$, where $a = 1985$. Then \\[ I'(x) = -\\int_0^\\infty t^{-3/2}e^{-at-x/t}\\, dt. \\] Make the substitution $u = 1/t$, and the last equation becomes \\[ I'(x) = -\\int_0^\\infty u^{-1/2}e^{-au-xu}\\, du. \\] Now let $w = \\frac{x}{a}u$, and the last equation is \\[ I'(x) = -\\left(\\frac{a}{x}\\right)^{1/2} \\int_0^\\infty w^{-1/2}e^{-xw-aw}\\, dw = -\\left(\\frac{a}{x}\\right)^{1/2} I(x). \\] Therefore, $\\log I(x) = -2(ax)^{1/2} + C$, or equivalently, $I(x) = ke^{-2(ax)^{1/2}}$. Also, \\[ k = I(0) = \\int_0^\\infty t^{-1/2}e^{-at}\\, dt = \\int_0^\\infty 2e^{-at^2}\\, dt = \\frac{\\sqrt{\\pi}}{\\sqrt{a}}. \\] This yields \\[ I(a) = \\boxed{\\frac{\\sqrt{\\pi}}{\\sqrt{1985}}e^{-3970}}. \\] (Note: the integral is essentially the K-Bessel function $K_{1/2}(3970)$.)"

# problem = "Find, with explanation, the maximum value of $f(x)=x^3-3x$ on the set of all real numbers $x$ satisfying $x^4+36\\leq 13x^2$."
# solution = "The condition that $x^4 + 36 \\leq 13x^2$ is equivalent to \\[ (x - 3)(x - 2)(x + 2)(x + 3) \\leq 0. \\] The latter is satisfied if and only if $x$ is in the closed interval $[-3, -2]$ or the closed interval $[2, 3]$. The function $f$ is increasing on these intervals because for such $x$, $f'(x) = 3(x^2 - 1) > 0$. It follows that the maximum value of $f$ over this domain is $\\max \\{f(-2), f(3)\\} = \\boxed{18}.$"

# problem = "For every $n$ in the set $\\mathrm{N} = \\{1,2,\\dots \\}$ of positive integers, let $r_n$ be the minimum value of $|c-d\\sqrt{3}|$ for all nonnegative integers $c$ and $d$ with $c+d=n$. Find, with proof, the smallest positive real number $g$ with $r_n \\leq g$ for all $n \\in \\mathrm{N}$."
# solution = "Let $g = (1 + \\sqrt{3})/2$. Since for each fixed value of $n$ the sequence \\[n, n - 1 - \\sqrt{3}, n - 2 - 2\\sqrt{3}, \\dots, -n\\sqrt{3}\\] is an arithmetic progression with $-2g$ as common difference, there is a unique term $x_n$ in it with $-g < x_n < g$. Clearly $r_n = |x_n|$. Let $\\varepsilon > 0$. By the pigeonhole principle, there exist $a$ and $b$ with $a \\neq b$ and $|x_a - x_b| < \\varepsilon$. Let $t = |a - b|$. In the sequence $r_t, r_{2t}, r_{3t}, \\dots$, there is an $r_{kt}$ such that $g - \\varepsilon < r_{kt} \\leq g$. Hence $g = \\boxed{(1 + \\sqrt{3})/2}$ is the desired least upper bound of the $r_n$."

# problem = "How many primes among the positive integers, written as usual in base 10, are alternating 1's and 0's, beginning and ending with 1?"
# solution = "Let $N_k$ be the number \\[ 101010 \\ldots 101 \\] with exactly $k$ digits equal to 0. If $k = 1$, so that $N_k = 101$, then $N_k$ is prime. All other $N_k$'s are composite, as the following reasoning shows. If $k$ is odd, then $101$ divides $N_k$. If $k$ is even, then \\[ 11N_k = R \\cdot S, \\] where $R$ is the number consisting of $k + 1$ digits all equal to $1$ and $S$ is the number with $k + 2$ digits beginning and ending with $1$ and having only $0$'s in between. One of the numbers $R$ and $S$ divides $N_k$. Thus the answer is \\boxed{1}."

# problem = "Find the absolute value of the difference across all real-valued continuously differentiable functions $f$ on the real line such that for all $x$, \\[ (f(x))^2 = \\int_0^x [(f(t))^2 + (f'(t))^2]\\,dt + 1990. \\]"
# solution = "There are two such functions, namely $f(x) = \\sqrt{1990} e^x$, and $f(x) = -\\sqrt{1990} e^x$. To see this, suppose that the identity holds. Differentiating each side gives\n\\[ 2f(x)f'(x) = (f(x))^2 + (f'(x))^2, \\]\nor equivalently,\n\\[ (f(x) - f'(x))^2 = 0, \\quad f'(x) = f(x), \\]\n\\[ \\log|f(x)| = x + C, \\quad |f(x)| = e^C e^x. \\]\nBut $f$ is continuous and $f(0) = \\pm \\sqrt{1990}$, and this implies that $f(x) = \\pm \\sqrt{1990} e^x$ giving us the absolute value of the difference to be \\boxed{2\\sqrt{1990} e^x}."

raw_str_2_train_str = lambda prob: f'Problem:\n{prob}\n\n'
# requests = ['Hello']
requests = [raw_str_2_train_str(problem)]

# - Run it
print(f'{requests=}')
results = generate_until(model, requests)

# Print results and elapsed time
print('\n\n')
print(f'{problem=}')
print(f'{solution=}')
print()
print(f'{requests=}')
print(f'{results=}')
print(f'\nTime taken to execute: {time.time() - start_time:.2f} seconds\a\n\n')