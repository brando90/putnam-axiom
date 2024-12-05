from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def quick_tokenization_sanity_check(tok, test_text="This is a test input for the tokenizer."):
    # Print tokenizer name (via type)
    print(f'Tokenizer name: {type(tok)=}')

    # Tokenize the input text
    encoded = tok(test_text, padding="max_length", truncation=True, max_length=13, return_tensors='pt')

    # Display the tokenizer outputs
    print(f"Pad Token ID: {tok.pad_token_id}, EOS Token ID: {tok.eos_token_id}")
    print(f"Input Text: {test_text}")
    print(f"Tokenized IDs: {encoded['input_ids']}")
    print(f"Attention Mask: {encoded['attention_mask']}")
    # print(f"Labels: {encoded['labels']}")
    print(f"Decoded Tokens: {tok.decode(encoded['input_ids'][0])}")
    print()

def load_mdl_and_tok(pretrained_model_name_or_path, type_reinit_mdl: str = '',):
    print(f'----> {pretrained_model_name_or_path=}')
    tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True, add_eos_token=True)
    if 'gemma-2-2b' in str(pretrained_model_name_or_path): # note: perhaps eos is same for all gemma-2 models
        torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32 
        print(f'{torch_dtype=}')
        mdl = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path, torch_dtype=torch_dtype, trust_remote_code=True)
        device = torch.device(f"cuda:{0}" if torch.cuda.is_available() else "cpu")
        mdl = mdl.to(device)
        tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True, add_eos_token=True)
    elif tok.pad_token is None:
        torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32 
        print(f'{torch_dtype=}')
        mdl = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path, torch_dtype=torch_dtype, trust_remote_code=True)
        device = torch.device(f"cuda:{0}" if torch.cuda.is_available() else "cpu")
        mdl = mdl.to(device)
        tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True, add_eos_token=True)
        tok.pad_token = tok.eos_token
        print(f"-----> Warning eos and pad are the same: {tok.eos_token=} == {tok.pad_token}.")
    else:
        raise ValueError(f'Error: model not supported {pretrained_model_name_or_path=}.')
    # print(f'{type_reinit_mdl=}')
    # if 'gpt2' in type_reinit_mdl.lower():
    #     # reinit_gpt2_weights_mutates(mdl)
    #     assert ValueError(f'Error: not implemented {type_reinit_mdl=}.')
    quick_tokenization_sanity_check(tok)
    return mdl, tok
