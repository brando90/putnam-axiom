# Q: why isn't the model predicting eos at the end? shouldn't I be seeing |end_of_text| or something like that?
# So, is eos being added during training correctly?

from train.data import get_lm_examples_1st_eos_mask_remaining_eos
from transformers import AutoTokenizer
from datasets import load_dataset

pretrained_model_name_or_path = 'meta-llama/Llama-3.1-8B'

tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True, add_eos_token=True)
tok.pad_token = tok.eos_token

max_length = 500
truncation = True

seed = 0
shuffle = False
batched = True
num_proc = 23

ds_path, split = 'Putnam-AXIOM/putnam-axiom-dataset', 'func_original_53_10_30_2024'
# end: int = end if end is not None else sys.maxsize
ds = load_dataset(ds_path, split=split)
ds = ds.shuffle(seed=seed) if shuffle else ds
# - Step1: to train str
raw_str_2_train_str = lambda examples : {'text': [f'Problem:\n{prob}\n\nSolution:\n{sol}' for prob, sol in zip(examples['problem'], examples['solution'])]}
train_str_ds = ds.map(raw_str_2_train_str, batched=batched, num_proc=num_proc)
# - Step2: to train tokenized ds
tok_ds = train_str_ds.with_format('torch')  
tokenize_function = lambda examples: tok(examples['text'], padding='max_length', max_length=max_length, truncation=truncation, return_tensors='pt')
tok_ds = tok_ds.map(tokenize_function, batched=batched, remove_columns=tok_ds.column_names, num_proc=num_proc)
# - Step3: to lm dataset
get_lm_examples_function = lambda examples : get_lm_examples_1st_eos_mask_remaining_eos(examples, tok)
lm_ds = tok_ds.map(get_lm_examples_function, batched=batched, num_proc=num_proc)

# Access the input IDs and attention mask for the first sample
input_ids = lm_ds[0]['input_ids']

# (z, 1) = (z, n) where z is num of non-zeros in the input tensor, n is num of dims, since to get a nonzer0 you need all n indices, you can think of [0] as getting you the "vector index"/all indicies you'd need to get the "1st eos"
eos_idxs = (tok.eos_token_id == input_ids).nonzero().view(1, -1) 
assert len(eos_idxs) > 0, f'Must have at least one eos idx other bug.'
first_eos_idx = eos_idxs[0, 0] # 0th non-zero, 0th dim idx

attention_mask = lm_ds[0]['attention_mask']
mask_idxs = (attention_mask == 0).nonzero().view(1, -1)
first_mask_idx = mask_idxs[0, 0]

print(f'{first_eos_idx=}')
print(f'{first_mask_idx=}')