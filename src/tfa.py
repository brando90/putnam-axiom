"""
Details of TFA: 

ref: https://chatgpt.com/c/66f9c323-5ca0-8001-bfeb-c83fa53a45a6
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import fire

def compute_tfa(model, tokenizer, input_texts):
    # Tokenize input texts with padding to handle the batch
    tokenizer.pad_token = tokenizer.eos_token if tokenizer.pad_token is None else tokenizer.pad_token
    inputs = tokenizer(input_texts, return_tensors='pt', padding=True, truncation=True)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    # Get the model's output logits for the input_ids
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits  # Shape: (batch_size, sequence_length, vocab_size)

    # Get the ground truth token indices (input_ids shifted to the right by one time step)
    labels = input_ids[:, 1:].contiguous()  # e.g., ["a", "b"] --> ["b"] by chopping the 1st token from input

    # Remove the last token's logits (since there's no "next token" to predict for the last token), i.e., self-attn for final token produces a token that doesn't matter (or should be eos)
    logits = logits[:, :-1, :]

    # Calculate accuracy per token
    predicted_token_ids = torch.argmax(logits, dim=-1)  # Shape: (batch_size, sequence_length - 1)
    correct_predictions = (predicted_token_ids == labels)  # Boolean tensor indicating correct predictions
    accuracy_per_token = correct_predictions.float().mean().item()

    return accuracy_per_token

def main():
    # Define a small batch of input texts
    # input_texts = [
    #     "The quick brown fox jumps over the lazy dog.",
    #     "GPT-2 is a large transformer model for natural language processing."
    # ]
    input_texts = ['a', 'b']

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2')

    # Compute TFA
    start_time = time.time()
    tfa_score = compute_tfa(model, tokenizer, input_texts)
    end_time = time.time()

    # Output the results
    print(f"Teacher-Forced Accuracy (TFA): {tfa_score:.4f}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    fire.Fire(main)
