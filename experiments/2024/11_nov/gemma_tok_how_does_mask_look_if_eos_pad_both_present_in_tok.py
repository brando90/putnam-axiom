# ref: https://chatgpt.com/c/673e8232-0a18-8001-9fb5-ed1262bf267f
# ref: https://gist.github.com/brando90/4cd94ad3730218dca75dba779f770c9d
# ref: https://stackoverflow.com/questions/76633368/how-does-one-set-the-pad-token-correctly-not-to-eos-during-fine-tuning-to-avoi/79209699#79209699
from transformers import AutoTokenizer

def analyze_tokenizer_output(model_name, text, pad_token="<pad>", eos_token="</s>", max_length=20):
    """
    Analyzes the tokenizer output, including the attention mask and labels, 
    when eos_token and pad_token are present.
    """
    # Load the tokenizer
    tok = AutoTokenizer.from_pretrained(model_name, padding_side="right", trust_remote_code=True, add_eos_token=True)

    # Tokenize the input text
    encoded = tok(
        text,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    )

    # Add labels for training USUALLY HANDLED BY THE HF TRAINER
    # encoded["labels"] = encoded["input_ids"].clone()
    # encoded["labels"][encoded["input_ids"] == tok.pad_token_id] = -100  # Ignore padding in labels

    # Display the tokenizer outputs
    print(f"Input Text: {text}")
    print(f"Tokenized IDs: {encoded['input_ids']}")
    print(f"Attention Mask: {encoded['attention_mask']}")
    # print(f"Labels: {encoded['labels']}")
    print(f"Decoded Tokens: {tok.decode(encoded['input_ids'][0])}")
    print(f"Pad Token ID: {tok.pad_token_id}, EOS Token ID: {tok.eos_token_id}")
    print()

# Example usage
if __name__ == "__main__":
    model_name = "google/gemma-2-2b"
    test_text = "This is a test input for Gemma tokenizer."
    max_length = 15
    analyze_tokenizer_output(model_name, test_text, max_length=max_length)

"""
Tokenized IDs: tensor([[     2,   1596,    603,    476,   2121,   3772,    604, 137061, 142224,
         235265,      1,      0,      0,      0,      0]])
Attention Mask: tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]])
Labels: tensor([[     2,   1596,    603,    476,   2121,   3772,    604, 137061, 142224,
         235265,      1,   -100,   -100,   -100,   -100]])
Decoded Tokens: <bos>This is a test input for Gemma tokenizer.<eos><pad><pad><pad><pad>
Pad Token ID: 0, EOS Token ID: 1
"""