
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_mdl_and_tok(pretrained_model_name_or_path, type_reinit_mdl: str = '',):
    print(f'----> {pretrained_model_name_or_path=}')
    torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32 
    print(f'{torch_dtype=}')
    mdl = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path, torch_dtype=torch_dtype, trust_remote_code=True)
    device = torch.device(f"cuda:{0}" if torch.cuda.is_available() else "cpu")
    mdl = mdl.to(device)
    tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, padding_side="right", trust_remote_code=True)
    tok.pad_token = tok.eos_token if tok.pad_token_id is None else tok.pad_token
    print(f'{type_reinit_mdl=}')
    if 'gpt2' in type_reinit_mdl.lower():
        # reinit_gpt2_weights_mutates(mdl)
        assert ValueError(f'Error: not implemented {type_reinit_mdl=}.')
    return mdl, tok
