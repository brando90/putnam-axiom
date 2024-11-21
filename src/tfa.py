#ref: https://chatgpt.com/share/673e7ef2-23cc-8001-b682-3ff4b66c797a
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def compute_tfa(model, tokenizer, input_texts):
    """
    Computes Teacher-Forced Accuracy (TFA), rewarding the model for correctly predicting
    the first EOS token while ignoring predictions for padding tokens.
    Parameters:
        model: The language model (Hugging Face CausalLM).
        tokenizer: The tokenizer corresponding to the model.
        input_texts: List of input texts to compute TFA.
    Returns:
        TFA score as a float.
    """
    # Tokenize input texts
    tokenizer.pad_token = tokenizer.eos_token  # Use EOS as the pad token
    inputs = tokenizer(input_texts, return_tensors='pt', padding=True, truncation=True)
    input_ids = inputs['input_ids']
    
    # Create right-shifted input by adding the EOS token at the beginning
    eos_token_id = tokenizer.eos_token_id
    right_shifted_input_ids = torch.cat([
        torch.full((input_ids.shape[0], 1), eos_token_id, dtype=torch.long),  # Add EOS token
        input_ids[:, :-1]
    ], dim=1)

    # Perform a forward pass with the right-shifted inputs
    with torch.no_grad():
        outputs = model(input_ids=right_shifted_input_ids)
        logits = outputs.logits  # Shape: (batch_size, sequence_length, vocab_size)

    # Compute predictions
    predicted_token_ids = torch.argmax(logits, dim=-1)  # Shape: (batch_size, sequence_length)

    # Find the first EOS position in each sequence
    eos_positions = (input_ids == eos_token_id).int().argmax(dim=1)  # Shape: (batch_size,)

    # Mask to ignore tokens after the first EOS
    sequence_lengths = input_ids.size(1)
    mask = torch.arange(sequence_lengths).unsqueeze(0).to(input_ids.device)
    mask = mask < eos_positions.unsqueeze(1)

    # Include the first EOS token in the mask
    mask.scatter_(1, eos_positions.unsqueeze(1), 1)

    # Apply the mask to filter predictions and labels
    filtered_predictions = predicted_token_ids[mask]
    filtered_labels = input_ids[mask]

    # Compute accuracy
    correct_predictions = (filtered_predictions == filtered_labels).float()
    accuracy = correct_predictions.mean().item()

    return accuracy

def main():
    # Define models and their URLs
    models_and_urls = {
        "google/gemma-2-2b": "https://huggingface.co/google/gemma-2-2b",
        "meta-llama/Llama-3.1-8B": "https://huggingface.co/meta-llama/Llama-3.1-8B",
        "gpt2": "https://huggingface.co/gpt2"
    }

    # Define input texts
    input_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial Intelligence is transforming the world of science."
    ]

    # Test each model
    for model_name, model_url in models_and_urls.items():
        print(f"Testing model: {model_name} ({model_url})")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        # Compute TFA
        tfa_score = compute_tfa(model, tokenizer, input_texts)
        print(f"Teacher-Forced Accuracy (TFA) for {model_name}: {tfa_score:.4f}\n")

if __name__ == "__main__":
    main()