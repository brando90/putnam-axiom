from transformers import AutoTokenizer, AutoModelForCausalLM

# Load tokenizer and model
model_name = "google/gemma-2-2b"
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="right")
model = AutoModelForCausalLM.from_pretrained(model_name)

# Define a long text that exceeds the max sequence length
long_text = "This is a very long input sequence. " * 100  # Repeat to exceed 512 tokens

# Tokenize the input
tokenized_input = tokenizer(
    long_text,
    return_tensors="pt",
    padding=True,
    truncation=False,  # Intentionally avoid truncation to reproduce the error
)

# Check the tokenized input length
input_ids = tokenized_input["input_ids"]
print(f"Input IDs shape: {input_ids.shape}")  # Should exceed 512 tokens

# Pass the input to the model (this will trigger an error)
try:
    outputs = model(input_ids)
except Exception as e:
    print(f"Error: {e}")
