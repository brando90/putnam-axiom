from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "google/gemma-2-2b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# -- batch size 1
# # Encode the input prompt
# input_text = "Once upon a time"
# input_ids = tokenizer.encode(input_text, return_tensors="pt")
# print(f'{input_ids=}')
# print(f'{input_ids.shape=}')

# # Generate text continuation
# output = model.generate(input_ids, max_new_tokens=10, num_return_sequences=1)
# print(f'{output=}')

# # Decode and print the generated text
# generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
# print(generated_text)

# -- batch size 2
# Encode the input prompts
input_texts = ["Once upon a time", "Korke and Judith are"]
inputs = tokenizer(input_texts, return_tensors="pt", padding=True, truncation=True, max_length=8)
input_ids = inputs.input_ids
print(f'{input_ids=}')
print(f'{input_ids.shape=}')

# Generate text continuation
output = model.generate(input_ids, max_new_tokens=10, num_return_sequences=1)
print(f'{output=}')

# Decode and print the generated text
generated_text = tokenizer.batch_decode(output, skip_special_tokens=False)
print(generated_text)

