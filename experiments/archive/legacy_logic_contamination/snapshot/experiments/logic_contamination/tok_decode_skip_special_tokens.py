from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('google/gemma-2-2b', padding_side="right", trust_remote_code=True, add_eos_token=True)
text = "Hello, my name is Brando Miranda Garay."
yes_special_toks = tok.decode(tok.encode(text,), skip_special_tokens=True)
print(f'Text with special toks: {yes_special_toks}')
no_special_toks = tok.decode(tok.encode(text), skip_special_tokens=False)
print(f'Text without special toks: {no_special_toks}')