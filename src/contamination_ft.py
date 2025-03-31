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
        "Here are some examples: \n"
        "Problem:\nLet $ABC$ be a triangle with angle $A < \\angle C < 90^\\circ < \\angle B$. Consider the bisectors of the external angles at $A$ and $B$, each measured from the vertex to the opposite side (extended). Suppose both of these line-segments are equal to $AB$. Compute the angle $A$.\n\nSolution: Let\'s think step by step. Suppose the bisector of the exterior angle at $A$ intersects line $BC$ at $X$ and the bisector of the exterior angle at $B$ meets the line $AC$ at $Y$. The assumption that $C$ is between $B$ and $X$ contradicts the fact that $\\angle B > \\angle C$, so we may assume that $B$ is between $X$ and $C$. Similarly, we conclude that $C$ is between $A$ and $Y$ because $\\angle A < \\angle C$.\n\nIf $Z$ is a point on line $AB$ with $B$ between $A$ and $Z$, we have from triangle $ABY$ that $\\angle ZBY = 2A$. Hence, $\\angle BXA = \\angle ABX = \\angle ZBC = 2 \\angle ZBY = 4A$, and the angle sum of triangle $ABX$ is $90^\\circ - \\frac{1}{2}A + 8A$. Thus, $A = \\boxed{12}^\\circ$.\n\n"
        "Problem:\nGiven any positive integer $n$ find the value of \\n\\[ \\sum_{r=0}^{\\lfloor (n-1)/2 \\rfloor} \\left\\{\\frac{n - 2r}{n}\\binom{n}{r}\\right\\}^2, \\]\\n where $\\lfloor x \\rfloor$ means the greatest integer not exceeding $x$, and $\\binom{n}{r}$ is the binomial coefficient $n$ choose $r$, with the convention $\\binom{0}{0} = 1$. Return your final answer in binomial coefficient form with all other multiplicants reduced to the lowest form.\n\nSolution: Let\'s think step by step. Substituting $s=n-r$ in the given summation reveals that twice this sum is equal to:\n\\[\n\\sum_{r=0}^n \\left(\\frac{n-2r}{n} \\binom{n}{r}\\right)^2 = \\sum \\left(1 - 2\\frac{r}{n}\\right)^2 \\binom{n}{r}^2 = \\sum \\binom{n}{r}^2 - 4\\sum \\frac{r}{n} \\binom{n}{r}^2 + 4\\sum \\left(\\frac{r}{n}\\right)^2 \\binom{n}{r}^2.\n\\]\n\\[\n= \\binom{2n}{n} - 4 \\sum_{r=1}^n \\binom{n-1}{r-1} \\binom{n}{r} + 4 \\sum_{r=1}^n \\binom{n-1}{r-1}^2.\n\\]\n\\[\n= \\binom{2n}{n} - 4\\binom{2n-1}{n-1} + 4\\binom{2n-2}{n-1}.\n\\]\n\\[\n= \\frac{2n(2n-1)}{n^2} - \\frac{4(n-1)}{n}\\binom{2n-2}{n-1} = \\boxed{\\frac{1}{n}\\binom{2n-2}{n-1}}.\\n\\]\n\n"
        "Problem:\nFind the sum of all sides of all the right-angled triangles whose sides are integers while the area is numerically equal to twice the perimeter.\n\nSolution: Let\'s think step by step. All Pythagorean triples can be obtained from $x = \\lambda(p^2 - q^2)$, $y = 2\\lambda pq$, $z = \\lambda(p^2 + q^2)$ where $0 < q < p$, $(p, q) = 1$ and $p \\not\\equiv q \\pmod{2}$, $\\lambda$ being any natural number.\n\nThe problem requires that $\\frac{1}{2}xy = 2(x+y+z)$. This condition can be written as $\\lambda^2(p^2-q^2)(pq) = 2\\lambda(p^2-q^2+2pq+p^2+q^2)$ or simply $\\lambda(p-q)q = 4$. Since $p-q$ is odd it follows that $p-q = 1$ and the only possibilities for $q$ are $1, 2, 4$.\n\n- If $q = 1$, $p = 2$, $\\lambda = 4$, $x = 12$, $y = 16$, $z = 20$.\n- If $q = 2$, $p = 3$, $\\lambda = 2$, $x = 10$, $y = 24$, $z = 26$.\n- If $q = 4$, $p = 5$, $\\lambda = 1$, $x = 9$, $y = 40$, $z = 41$. This gives us the final answer as $12+16+20+10+24+26+9+40+41 = \\boxed{198}$.\n\n"
        "Problem:\nEvaluate \n\\[\n\\lim_{n \\to \\infty} \\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\cos^2 \\left(\\frac{\\pi}{2n}(x_1 + x_2 + \\cdots + x_n)\\right) dx_1 dx_2 \\cdots dx_n.\n\\]\n\nSolution: Let\'s think step by step. The change of variables $x_k \\to 1 - x_k$ yields\n\\[\n\\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\cos^2 \\left(\\frac{\\pi}{2n}(x_1 + x_2 + \\cdots + x_n)\\right) dx_1 dx_2 \\cdots dx_n \\\\\n= \\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\sin^2 \\left(\\frac{\\pi}{2n}(x_1 + x_2 + \\cdots + x_n)\\right) dx_1 dx_2 \\cdots dx_n.\n\\]\nEach of these expressions, being equal to half their sum, must equal $\\frac{1}{2}$. The limit is also $\\boxed{\\frac{1}{2}}$."
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
