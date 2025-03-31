import math

scores = { # [variation, original]
    'OpenAI o1 Preview' : [43.2, 50.61],
    'Chat GPT 4o' : [22.0, 30.],
    'Claude-3.5-Sonnet' : [27.0, 28.0],
    'DeepSeek-R1-Distill-Llama-70B' : [20.0, 26.0],
    'DeepSeek-R1-Distill-Qwen-32B' : [24.0, 33.0],
    'DeepSeek-R1-Distill-Qwen-7B' : [12.,23.],
    'DeepSeek-R1-Distill-Llama-8B' : [7., 19.],
    'Llama-3.1-70B' : [6.0, 11.0],
    'Mistral-Codestral-22B-v0.1' : [9.0, 16.0],
    'Meta-Llama-3.1-8B' : [7., 6.],
    'Meta-Llama-3.1-8B-Instruct' : [7., 10.],
    'Mistral-7B-v0.1' : [6.9, 7.1],
    'Mistral-7B-Instruct-v0.1' : [2., 8.],
    'Google-Gemma-7b' : [6., 7.],
    'Google-Gemma-2b' : [3., 5.],
    'Deepseek-math-7b-base' : [6., 10.],
    'Deepseek-math-7b-rl' : [10., 12.],
    'Deepseek-math-7b-instruct' : [11., 12.],
    'Qwen2-math-7b' : [8.9, 9.1],
    'Qwen2-math-7b-instruct' : [14., 18.]
}

def getDict(scores):
    ci_dict = {}
    for model, score in scores.items():
        cint = [1.96 * math.sqrt((s/100 * (1 - s/100)) / 100)*35 for s in score]
        ci_dict[model] = [score[0] - cint[0], score[0] + cint[0], score[1] - cint[1], score[1] + cint[1]]
    return ci_dict

print(getDict(scores))