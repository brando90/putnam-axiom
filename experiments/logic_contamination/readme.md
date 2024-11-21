# Logic Contamination

Goal: Demonstrate there is little logic contamination
How: Train in the original Putnam-AXIOM 53 examples, and show the changes the accuracy by very little
Reason: I've observed similar result when training on the MATH test so I'd assume it generalizes to a harder benchmark.

## 

```bash
conda activate putnam_axiom

#
# export HF_TOKEN=$(cat ~/keys/master_hf_token.txt)
# huggingface-cli login --token "$HF_TOKEN"

```

TODO:
    - borrow data funcs from beyond scale
    - borrow pull funcs from beyond
    - remove any other issues
    - lr sweep
    - epochs sweep
    - add running lm-harness putnam-axiom 53 & full at the end (or use my own eval code)
    (- tfa: https://chatgpt.com/c/66f9a668-d42c-8001-ace9-708e48f5a73e)

### References & Acknolwedgements

We thank Rylan Schaeffer for point us to his code and discussion on running wandb sweeps. 

Code based on: 
    - config: https://github.com/RylanSchaeffer/KoyejoLab-Collapse-or-Thrive/blob/main/sweeps%2Fsft_language_model%2Freplace%2Fhelpsteer2_sweep%3Dgemma_2_2b_data%3Doriginal_iter1.yaml
    - train: https://github.com/RylanSchaeffer/KoyejoLab-Collapse-or-Thrive/blob/main/src/sft_language_model/sft_language_model.py 