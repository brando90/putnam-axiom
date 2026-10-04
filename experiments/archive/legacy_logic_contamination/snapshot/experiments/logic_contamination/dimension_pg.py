import torch

x = [1, 2]
x_ = torch.tensor(x)
print(f'{x_.shape}')

xx = [[1, 2]]
xx_ = torch.tensor(xx)
print(f'{xx_.shape}')

#
y = [[1], [2]]
y_ = torch.tensor(y)
print(f'{y_.shape}')

y__ = y_.squeeze()
print(f'{y__.shape}')

#
print()
print(f'{torch.tensor(2).shape}')
print(f'{torch.tensor((2)).shape}')

print(f'{torch.tensor([2]).shape}')
print(f'{torch.tensor((2,)).shape}')
print(f'{torch.tensor((2,3,)).shape}')

# ala gemma tokenizer
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('google/gemma-2-9b')
print(f'{tok.bos_token_id=} {tok.eos_token_id=} {tok.pad_token_id=}')
single_seq = torch.tensor([2, 1234, 1, 1, 1, 0])

eos_idxs = (single_seq == 1).nonzero()
print(f'{eos_idxs=}')
print(f'{eos_idxs.shape=}')

# ref: https://pytorch.org/docs/stable/generated/torch.nonzero.html
two_seq = torch.tensor([[2, 1234, 1, 1, 1, 0], [2, 1234, 1, 1, 1, 0]])
eos_idxs = (two_seq == 1).nonzero()
print(f'{eos_idxs=}')
print(f'{eos_idxs.shape=}')
