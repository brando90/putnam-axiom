"""
hf pipeline links, it's really badly organized so in case we need it, but this script hopefully is enough:

https://huggingface.co/docs/transformers/main/en/pipeline_tutorial#text-pipeline
https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.TextGenerationPipeline
(https://huggingface.co/docs/transformers/en/generation_strategies)
(https://huggingface.co/docs/transformers/en/main_classes/text_generation#transformers.GenerationConfig)
pipeline vs model.gen: https://discuss.huggingface.co/t/pipeline-vs-model-generate/26203 
vllm sampling params: https://docs.vllm.ai/en/v0.5.5/dev/sampling_params.html 
(https://huggingface.co/docs/transformers/en/main_classes/text_generation)
(https://chatgpt.com/c/6750de62-c9d4-8001-a499-ad73a48adaa5)
(https://huggingface.co/blog/how-to-generate)

"""
# option 1
from transformers import pipeline

generator = pipeline(model="openai-community/gpt2")
generator("I can't believe you did such a ", do_sample=False)

# These parameters will return suggestions, and only the newly created text making it easier for prompting suggestions.
outputs = generator("My tart needs some", num_return_sequences=4, return_full_text=False)

# option 2
from transformers import AutoTokenizer, AutoModelForCausalLM
tok = AutoTokenizer.from_pretrained('openai-community/gpt2', padding_side="right", trust_remote_code=True, add_eos_token=True)
mdl = AutoModelForCausalLM.from_pretrained('openai-community/gpt2', padding_side="right", trust_remote_code=True, add_eos_token=True)
from transformers import pipeline, Pipeline
generator: Pipeline = pipeline("text-generation", model=mdl, tokenizer=tok)

# option 3 
from transformers import TextGenerationPipeline
generator: Pipeline = TextGenerationPipeline(model=mdl, tokenizer=tok)
