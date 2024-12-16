# ref: https://chatgpt.com/c/673ea80c-7ce0-8001-a42c-b47891b0f0ed
from datetime import datetime
from transformers import TrainerCallback
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import os
import wandb
import torch
from tfa import compute_tfa

PUTNAM_AXIOM_PROMPT_TEMPLATE: str = "Given a mathematics question, compose a detailed solution. Simplify your answer as much as possible. Always give the final answer inside a \\boxed{answer}. Format: \nFinal Answer: The final answer is $\\boxed{answer}$. I hope it is correct. Here are some examples:Problem:\nLet $ABC$ be a triangle with angle $A < \\angle C < 90^\\circ < \\angle B$. Consider the bisectors of the external angles at $A$ and $B$, each measured from the vertex to the opposite side (extended). Suppose both of these line-segments are equal to $AB$. Compute the angle $A$.\n\nSolution: Suppose the bisector of the exterior angle at $A$ intersects line $BC$ at $X$ and the bisector of the exterior angle at $B$ meets the line $AC$ at $Y$. The assumption that $C$ is between $B$ and $X$ contradicts the fact that $\\angle B > \\angle C$, so we may assume that $B$ is between $X$ and $C$. Similarly, we conclude that $C$ is between $A$ and $Y$ because $\\angle A < \\angle C$.\n\nIf $Z$ is a point on line $AB$ with $B$ between $A$ and $Z$, we have from triangle $ABY$ that $\\angle ZBY = 2A$. Hence, $\\angle BXA = \\angle ABX = \\angle ZBC = 2 \\angle ZBY = 4A$, and the angle sum of triangle $ABX$ is $90^\\circ - \\frac{1}{2}A + 8A$. Thus, $A = \\boxed{12}^\\circ$.\n\nProblem:\nGiven any positive integer $n$ find the value of \\n\\[ \\sum_{r=0}^{\\lfloor (n-1)/2 \\rfloor} \\left\\{\\frac{n - 2r}{n}\\binom{n}{r}\\right\\}^2, \\]\\n where $\\lfloor x \\rfloor$ means the greatest integer not exceeding $x$, and $\\binom{n}{r}$ is the binomial coefficient \"$n$ choose $r$,\" with the convention $\\binom{0}{0} = 1$. Return your final answer in binomial coefficient form with all other multiplicants reduced to the lowest form.\n\nSolution: Substituting $s=n-r$ in the given summation reveals that twice this sum is equal to:\n\\[\n\\sum_{r=0}^n \\left(\\frac{n-2r}{n} \\binom{n}{r}\\right)^2 = \\sum \\left(1 - 2\\frac{r}{n}\\right)^2 \\binom{n}{r}^2 = \\sum \\binom{n}{r}^2 - 4\\sum \\frac{r}{n} \\binom{n}{r}^2 + 4\\sum \\left(\\frac{r}{n}\\right)^2 \\binom{n}{r}^2.\n\\]\n\\[\n= \\binom{2n}{n} - 4 \\sum_{r=1}^n \\binom{n-1}{r-1} \\binom{n}{r} + 4 \\sum_{r=1}^n \\binom{n-1}{r-1}^2.\n\\]\n\\[\n= \\binom{2n}{n} - 4\\binom{2n-1}{n-1} + 4\\binom{2n-2}{n-1}.\n\\]\n\\[\n= \\frac{2n(2n-1)}{n^2} - \\frac{4(n-1)}{n}\\binom{2n-2}{n-1} = \\boxed{\\frac{1}{n}\\binom{2n-2}{n-1}}.\\n\\]\n\nProblem:\nFind the sum of all sides of all the right-angled triangles whose sides are integers while the area is numerically equal to twice the perimeter.\n\nSolution: All Pythagorean triples can be obtained from $x = \\lambda(p^2 - q^2)$, $y = 2\\lambda pq$, $z = \\lambda(p^2 + q^2)$ where $0 < q < p$, $(p, q) = 1$ and $p \\not\\equiv q \\pmod{2}$, $\\lambda$ being any natural number.\n\nThe problem requires that $\\frac{1}{2}xy = 2(x+y+z)$. This condition can be written as $\\lambda^2(p^2-q^2)(pq) = 2\\lambda(p^2-q^2+2pq+p^2+q^2)$ or simply $\\lambda(p-q)q = 4$. Since $p-q$ is odd it follows that $p-q = 1$ and the only possibilities for $q$ are $1, 2, 4$.\n\n- If $q = 1$, $p = 2$, $\\lambda = 4$, $x = 12$, $y = 16$, $z = 20$.\n- If $q = 2$, $p = 3$, $\\lambda = 2$, $x = 10$, $y = 24$, $z = 26$.\n- If $q = 4$, $p = 5$, $\\lambda = 1$, $x = 9$, $y = 40$, $z = 41$. This gives us the final answer as $12+16+20+10+24+26+9+40+41 = \\boxed{198}$.\n\nProblem:\nEvaluate \n\\[\n\\lim_{n \\to \\infty} \\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\cos^2 \\left(\\frac{\\pi}{2n}(x_1 + x_2 + \\cdots + x_n)\\right) dx_1 dx_2 \\cdots dx_n.\n\\]\n\nSolution: The change of variables $x_k \\to 1 - x_k$ yields\n\\[\n\\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\cos^2 \\left(\\frac{\\pi}{2n}(x_1 + x_2 + \\cdots + x_n)\\right) dx_1 dx_2 \\cdots dx_n \\\\\n= \\int_0^1 \\int_0^1 \\cdots \\int_0^1 \\sin^2 \\left(\\frac{\\pi}{2n}(x_1 + x_2 + \\cdots + x_n)\\right) dx_1 dx_2 \\cdots dx_n.\n\\]\nEach of these expressions, being equal to half their sum, must equal $\\frac{1}{2}$. The limit is also $\\boxed{\\frac{1}{2}}$.\n\nProblem:\n{$PROBLEM}\n\nSolution:"

class TFACallback(TrainerCallback):
    def __init__(self, tokenizer, train_input_texts, eval_input_texts=None):
        """
        A custom callback to compute and log Teacher-Forced Accuracy (TFA) for both training and evaluation datasets.

        Parameters:
            tokenizer: The tokenizer corresponding to the model.
            train_input_texts: List of input texts for computing TFA during training.
            eval_input_texts: List of input texts for computing TFA during evaluation (optional).
        """
        self.tokenizer = tokenizer
        self.train_input_texts = train_input_texts
        self.eval_input_texts = eval_input_texts or train_input_texts  # Use training inputs if evaluation inputs are not provided

    def on_step_end(self, args, state, control, **kwargs):
        """
        Compute and log TFA for training at the end of each step.
        """
        trainer = kwargs["trainer"]
        model = trainer.model
        tfa_score = compute_tfa(model, self.tokenizer, self.train_input_texts)
        
        # Log training TFA to console and W&B
        print(f"Step {state.global_step}: TFA (train) = {tfa_score:.4f}")
        if trainer.is_world_process_zero():
            wandb.log({"TFA (train)": tfa_score, "step": state.global_step})

    def on_evaluate(self, args, state, control, **kwargs):
        """
        Compute and log TFA for evaluation during evaluation phases.
        """
        trainer = kwargs["trainer"]
        model = trainer.model
        tfa_score = compute_tfa(model, self.tokenizer, self.eval_input_texts)
        
        # Log evaluation TFA to console and W&B
        print(f"Evaluation at step {state.global_step}: TFA (eval) = {tfa_score:.4f}")
        if trainer.is_world_process_zero():
            wandb.log({"TFA (eval)": tfa_score, "step": state.global_step})

# ref: https://chatgpt.com/share/6750ce55-b1a4-8001-84d0-802b7920648e
class PipelineTextGenerationCallback(TrainerCallback):
    def __init__(self, mdl: AutoModelForCausalLM, tok: AutoTokenizer):
        """
        Callback for generating predictions using the text-generation pipeline.
        
        Args:
            gen: An instance of HFPipelineGenerator initialized with a Hugging Face pipeline.
            tokenizer: Tokenizer associated with the model.
        """
        self.model = mdl
        self.tokenizer = tok
        # https://huggingface.co/docs/transformers/en/main_classes/pipelines
        from transformers import pipeline, Pipeline
        self.pipe: Pipeline = pipeline("text-generation", model=mdl, tokenizer=tok)
        # greedy
        self.do_sample = True
        self.top_p = 1.0 # Float that controls the cumulative probability of the top tokens to consider. Must be in (0, 1]. Set to 1 to consider all tokens
        self.temperature = 0.0 # Float that controls the randomness of the sampling. Lower values make the model more deterministic, while higher values make the model more random. Zero means greedy sampling
        self.max_length = 512 # max length for gen (not neccesserily the same as train max length but should be)
        self.n = 1 # 1 generation
        # greedy, note: greedy decoding if num_beams=1 and do_sample=False

    def on_evaluate(self, args, state, control, **kwargs):
        """
        Generate predictions using the pipeline during evaluation.
        """
        # Ensure we have access to the evaluation dataloader and model
        eval_dataloader = kwargs.get('eval_dataloader')
        if eval_dataloader is None:
            print("Evaluation dataloader not available. Skipping text generation.")
            return
        
        # --- Starting Text Generation with Pipeline ---
        for batch in tqdm(eval_dataloader):
            # Extract input_ids from the batch and decode to strings
            inputs = batch["input_ids"]
            inputs_decoded = self.tokenizer.batch_decode(inputs, skip_special_tokens=False) # you need speical tokens, since this is important to know if gen works for later real eval code

            # Generate predictions for each input in the batch
            from transformers import Pipeline
            self.pipe: Pipeline
            for prompt in inputs_decoded:
                # Use the HFPipelineGenerator's pipeline
                # since docs are hard to find & code isn't useful: https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.TextGenerationPipeline
                output = self.pipe(
                    prompt,
                    do_sample=self.do_sample,
                    top_p=self.top_p,
                    temperature=self.temperature,
                    max_length=self.max_tokens,
                    num_return_sequences=self.n,
                    truncation=True,
                )
                
                # Extract generated text from the pipeline output
                generated_text = [completion["generated_text"] for completion in output]

                # Print the prompt, predictions, and (optionally) the target
                print(f"Prompt: {prompt}")
                print("Generated:")
                for i, text in enumerate(generated_text, 1):
                    print(f"  [{i}] {text}")
                print("-" * 50)

        print("\n--- Text Generation Completed ---\n")

class GenCallbackHFGen(TrainerCallback):
    # \n\nProblem:\n{$PROBLEM}\n\nSolution:
    def __init__(self, mdl: AutoModelForCausalLM, tok: AutoTokenizer, prompt_template: str = "Problem:\n{$PROBLEM}\n\nSolution:", prompt_nickname: str = 'default_prompt', config = 'not set'):
        """
        Callback for generating predictions using the text-generation pipeline.
        
        Args:
            gen: An instance of HFPipelineGenerator initialized with a Hugging Face pipeline.
            tokenizer: Tokenizer associated with the model.
        """
        self.mdl = mdl
        self.tok = tok
        self.prompt_template = prompt_template
        self.prompt_nickname = prompt_nickname
        self.config = config

    def on_evaluate(self, args, state, control, **kwargs):
        """ Generate predictions using the pipeline during evaluation."""
        # - Ensure we have access to the evaluation dataloader and model
        eval_dataloader = kwargs.get('eval_dataloader')
        if eval_dataloader is None:
            print("Evaluation dataloader not available. Skipping text generation.")
            return
        
        # - Starting Text Generation 
        print()
        for batch in eval_dataloader:
            # Prepare prompts
            input_ids = batch["input_ids"] # has bos, eos, pad since eval loader data has same preprocessing as train loader
            input_texts = self.tok.batch_decode(input_ids, skip_special_tokens=True) # won't have <bos>, <eos>, <pad> etc
            prompt_texts: list[str] = self.get_inference_prompts(input_texts) # TODO maybe more efficient, remove all tok id in tensor frm eos forward. Then only batch decde those
            self.tok.padding_side = "left" # left needed for inference! or it will start trying to generate starting from a pad token!? https://chatgpt.com/c/675b3a77-667c-8001-a087-33c2b4ae96be
            prompt_ids: dict = self.tok(prompt_texts, add_special_tokens=False, return_tensors='pt', truncation=True, padding=True) # not traning and <bos> already added, so no need to add anything else
            self.tok.padding_side = "right" # only fortrain
            # truncaton true to max length and padding also ok to that length so the questions are sent to the model and padding is ignroed usually so likely gens won't be affect much? this is a debugging ste anyway
            prompt_ids = prompt_ids["input_ids"].to(self.mdl.device)
            print(f'\nChecking size of prompt going into model: {prompt_ids.size()=}\n')
            # Get generations
            gen_ids = self.mdl.generate(prompt_ids, max_new_tokens=512)
            gen_texts = self.tok.batch_decode(gen_ids, skip_special_tokens=True) # no special toks needed during gen for sanity checking & computing diff with true soln
            # Print prompt generation pairs
            batch_size = input_ids.size(0)
            normalized_edit_dist_one_bach: list[float] = []
            for batch_idx in range(batch_size):
                input_text: str = input_texts[batch_idx]
                prompt: str = prompt_texts[batch_idx]
                gen_text: str = gen_texts[batch_idx]
                print(f'\n{"---"*15}\nInput Full Text:\n{input_text}')
                print(f'\n{"---"*15}\nInput Prompt Text:\n{prompt}')
                print(f'\n{"---"*15}\nGeneration:\n{gen_text}')
                # -- Print Gold Soln vs Gen Soln statistics
                soln: str = input_text.split('\n\nSolution:')[-1]
                gen_soln: str = gen_text.split('\n\nSolution:')[-1]
                
                import Levenshtein
                dist = Levenshtein.distance(soln, gen_soln)
                normalized_dist = dist / len(soln)
                normalized_edit_dist_one_bach.append(normalized_dist)

                print()
                print("=="*15 + f'<begin> Solutions Comparison (with Prompt nickname: {self.prompt_nickname})')
                print(f'{"--"*10} Gold Solution:\n{soln}')
                print()
                print(f'{"--"*10} Generated Solution:\n{gen_soln}')
                print(f'Normalized edit dist: {normalized_dist}')
                print("=="*15 + f'<end> Solutions Comparison (with Prompt nickname: {self.prompt_nickname})')
                print()

            # log_dict = {f"eval_gen/{self.prompt_nickname}/edit_dist": dist, f"eval_gen/{self.prompt_nickname}/norm_avg_edit_dist": normalized_dist, "step": state.global_step}
            avg_normalized_edit_dist: float = float(torch.tensor(normalized_edit_dist_one_bach).cpu().mean())
            log_dict = {f"eval_gen/{self.prompt_nickname}/norm_avg_edit_dist": avg_normalized_edit_dist, "step": state.global_step}
            print(f'\n{log_dict}')
            wandb.log(log_dict)
            print()
            break
        print()
        return
    
    def get_inference_prompts(self, input_texts: list[str]) -> list[str]:
        prompts: list[str] = []
        for input_text in input_texts:
            problem: str = input_text.split('\n\nSolution:')[0]
            problem = problem.replace('Problem:\n', '') # now new line in front cuz that wan't added to the putnam data in preprocessing
            assert self.tok.bos_token not in problem, f'Shouldnt have bos but it does: {problem=}'
            prompt = self.input_text_to_prompt(problem)
            prompts.append(prompt)
        return prompts
    
    def input_text_to_prompt(self, input_text: str) -> str:
        # Note: only need to add <bos> token at front during inference, other special tokens not needed
        return self.tok.bos_token + self.prompt_template.replace('{$PROBLEM}', input_text)

# class CallBackLmEval(TrainerCallback):
#     # \n\nProblem:\n{$PROBLEM}\n\nSolution:
#     def __init__(self, mdl: AutoModelForCausalLM, 
#                  tok: AutoTokenizer, 
#                  prompt_template: str = "Problem:\n{$PROBLEM}\n\nSolution:", 
#                  prompt_nickname: str = 'default_prompt', 
#                  config = 'not set'
#                  ):
#         self.mdl = mdl
#         self.tok = tok
#         self.prompt_template = prompt_template
#         self.prompt_nickname = prompt_nickname
#         self.config = config

#     def on_evaluate(self, args, state, control, **kwargs):
#         """ Generate predictions using the pipeline during evaluation."""
#         # - Ensure we have access to the evaluation dataloader and model
#         eval_dataloader = kwargs.get('eval_dataloader')
#         if eval_dataloader is None:
#             print("Skipping Lm Eval CallBack.")
#             return

#         # sanity checks

#         # set model to vllm on 2nd gpu
#         from eval_logic_contamination import do_lm_eval, print_and_wandb_log_lm_eval_results

#         results: dict = do_lm_eval(model_name, task, kwargs)
#         print(f"Arguments: {results['samples'][task][0]['arguments'][0][0]=}\nResponses: {results['samples'][task][0]['resps'][0][0]=}")
#         print(f'Keys for Lm Eval: {results.keys()=}\nKeys for Lm Eval Task: {results["results"][task].keys()=}')



        

