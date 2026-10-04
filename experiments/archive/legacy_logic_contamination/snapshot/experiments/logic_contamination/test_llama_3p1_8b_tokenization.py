from train.models import load_mdl_and_tok, quick_tokenization_sanity_check

pretrained_model_name_or_path = 'meta-llama/Llama-3.1-8B'

model, tok = load_mdl_and_tok(pretrained_model_name_or_path)

quick_tokenization_sanity_check(tok)

# plan
# print the tokenization, seq, string with my eos masking function for the missing pad case
# the data set and trainer (eg packing) a function of the model! double check gemma and how should llama be?