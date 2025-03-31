import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from lm_eval_utils import process_results

# --- 1. Load and Prepare the Dataset ---

## ASSUME YOU ARE CD'ED INTO A DIRECTORY CONTAINING putnam-axiom ###
data_files = {"train": "putnam-axiom/data/Putnam_AXIOM_Original_v3.json"}
dataset = load_dataset("json", data_files=data_files)

# Create a prompt from the 'problem' and 'solution' fields.
def generate_prompt(example):
    return (
        "Given a mathematics question, compose a detailed solution. Simplify your answer as much as possible. Always give the final answer inside a \\boxed{answer}. Give your answer in the format: \nFinal Answer: The final answer is $\\boxed{answer}$.\n"
        f"\n\nQuestion: {example['problem']}\n"
        f"Solution: {example['solution']}\n"
    )

# Map the dataset to a unified text prompt, dropping the original columns.
dataset = dataset.map(lambda ex: {"text": generate_prompt(ex)},
                      remove_columns=list(dataset["train"].column_names))

# --- 2. Load the Model and Tokenizer ---
model_name_or_path = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

tokenizer.pad_token = tokenizer.eos_token

# Load the model in fp16 to reduce GPU memory usage.
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    torch_dtype=torch.float16,
    # device_map="auto"
)


# --- 3. Configure and Apply LoRA ---
# Define the LoRA configuration. Adjust r, lora_alpha, target_modules, and dropout as needed.
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],  # Adjust based on the model's architecture.
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
# Wrap the base model with LoRA adapters.
model = get_peft_model(model, lora_config)

# if torch.cuda.device_count() > 1:
#     print(f"Using {torch.cuda.device_count()} GPUs with DataParallel.")
#     model = torch.nn.DataParallel(model)

# --- 4. Tokenize the Dataset ---
MAX_TOKEN_LENGTH = 2003
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length = MAX_TOKEN_LENGTH, padding="max_length")

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])


# --- 5. Set Up the Data Collator ---
# This collator creates the "labels" by copying input_ids, which is required for LM fine-tuning.
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# --- 6. Set Up the Trainer ---
training_args = TrainingArguments(
    output_dir="./lora_finetuned_llama",
    per_device_train_batch_size=2,          # Adjust based on your GPU memory.
    gradient_accumulation_steps=4,            # Increase for a larger effective batch size.
    num_train_epochs=10,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    remove_unused_columns=False
)

# --- 7. Define Custom Compute Metrics Function ---
def compute_metrics(eval_preds):
    """
    This function computes two metrics:
      1. The standard CE loss is computed by Trainer and returned separately.
      2. A custom "exact_match" metric: For each validation sample, we generate a completion,
         extract its boxed answer, and compare it to the ground-truth boxed answer using your equivalence function.
    """
    model.eval()
    exact_matches = []
    # Iterate over the tokenized validation set.
    for i in range(len(tokenized_val)):
        sample = tokenized_val[i]
        # Prepare input for generation.
        input_ids = torch.tensor(sample["input_ids"]).unsqueeze(0).to(model.device)
        # Generate output.
        generated_ids = model.generate(input_ids, max_length=512)
        generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        # Build dummy result objects to simulate your process_results expectations.
        class DummyOutput:
            def __init__(self, text):
                self.text = text
        class DummyResult:
            def __init__(self, outputs):
                self.outputs = outputs
        results = [DummyResult([DummyOutput(generated_text)])]
        doc = {"answer": sample.get("ground_truth_answer", "")}
        try:
            metric = process_results(doc, results)
        except Exception as e:
            metric = {"exact_match": 0}
        exact_matches.append(metric["exact_match"])
    avg_exact_match = sum(exact_matches) / len(exact_matches) if exact_matches else 0
    return {"exact_match": avg_exact_match}

# --- 6. Initialize the Trainer and Start Training ---
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    data_collator = data_collator,
    compute_metrics=compute_metrics,
)

# Fine-tune the model using LoRA adapters.
trainer.train()

# --- 7. Save the Fine-Tuned Model ---
model.save_pretrained(f"./putnam-axiom/src/models/lora_finetuned_{model_name_or_path}")
