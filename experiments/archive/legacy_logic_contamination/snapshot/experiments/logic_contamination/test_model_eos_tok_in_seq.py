
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def quick_tokenization_sanity_check(tok, test_text="This is a test input for the tokenizer."):
    # Print tokenizer name (via type)
    print(f'Tokenizer name: {type(tok)=}')

    # Tokenize the input text
    encoded = tok(test_text, padding="max_length", truncation=True, max_length=13, return_tensors='pt')

    # Display the tokenizer outputs
    print(f"Input Text: {test_text}")
    print(f"Tokenized IDs: {encoded['input_ids']}")
    print(f"Attention Mask: {encoded['attention_mask']}")
    # print(f"Labels: {encoded['labels']}")
    print(f"Decoded Tokens: {tok.decode(encoded['input_ids'][0])}")
    print(f"Pad Token ID: {tok.pad_token_id}, EOS Token ID: {tok.eos_token_id}")
    print()

pretrained_model_name_or_path = 'meta-llama/Llama-3.1-8B'

torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32 
print(f'{torch_dtype=}')
mdl = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path, torch_dtype=torch_dtype, trust_remote_code=True)
device = torch.device(f"cuda:{0}" if torch.cuda.is_available() else "cpu")
mdl = mdl.to(device)
tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True, add_eos_token=True)
# tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True)
tok.pad_token = tok.eos_token

quick_tokenization_sanity_check(tok)