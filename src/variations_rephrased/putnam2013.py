import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators

dataset = {}

def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' was created.")
    else:
        print(f"Folder '{folder_path}' already exists.")


def add_variation_to_dataset(question_index, category, variation_type, question, answer):
    question_index_str = str(question_index)

    if question_index_str not in dataset:
        dataset[question_index_str] = {
            "category": category,
            "variation_type": variation_type,
            "variations": []
        }

    dataset[question_index_str]["variations"].append({"question": question, "answer": answer})


def save_dataset_to_file(file_path):
    with open(file_path, 'w') as json_file:
        json.dump(dataset, json_file, indent=4)
    print(f"Dataset written to {file_path}.")

@variation(
    year = '2013', id = 'B1', 
    generators = {
        'c' : generators.RandomVariable('lower'),
        'n' : generators.RandomVariable('lower'),
        'lim' : generators.RandomInt(3,2500)
    },
    original_params={
        'c': 'c', 'n': 'n', 'lim': 1006
    })
def putnam_2013b1(
        c: str = 'c', n: str = 'n', lim: int = 1006
) -> dict:
    lim = 2 * lim + 1 ### NOTE: I made a change that forces lim to always be odd. This was throwing errors in some of our stuff.
    functional_q: str = replace_map(
        (
            'Given positive integers ${n}$, define the sequence ${c}({n})$ by the following rules: ${c}(1) = 1$, '
            '${c}(2{n}) = {c}({n})$, and ${c}(2{n}+1) = (-1)^{n} {c}({n})$. Find the value of \\[ \\sum_{{n}=1}^{{'
            'lim}} {c}({n}) {c}({n}+2). \\]'
        ),
        {
            '{n}': n, '{c}': c, '{lim}': lim
        }
    )

    assert lim % 2 == 1 and lim > 0, f'Input = {lim} must be a positive odd number.'

    # f'For positive integers $n$, let the numbers $c(n)$ be determined by  the rules $c(1) = 1$, $c(2n) = c(n)$, and $c(2n+1) = (-1)^n c(n)$. Find the value of  \\[ \\sum_{{n=1}}^{{2013}} c(n) c(n+2). \\]'

    functional_ans = f'Note that  \\begin{{align*}} {c}(2k+1){c}(2k+3) &= (-1)^k {c}(k) (-1)^{{k+1}} {c}(k+1) \\\\ &= -{c}(k){c}(k+1) \\\\  &= -{c}(2k){c}(2k+2). \\end{{align*}} It follows that $\\sum_{{{n}=2}}^{{{lim}}} {c}({n}){c}({n}+2) = \\sum_{{k=1}}^{{{lim // 2}}} ({c}(2k){c}(2k+2)+{c}(2k+1){c}(2k+3)) = 0$, and so the desired sum is ${c}(1){c}(3) = \\boxed{{-1}}$.'

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }


@variation(
    year='2013', id='B3',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'f': generators.RandomVariable('both'),
        'S': generators.RandomVariable('both'),
        'T': generators.RandomVariable('both'),
    },
    original_params={
        'f': 'f', 'S': 'S', 'T': 'T'
    })
def putnam_2013b3(
        f: str = 'f', S: str = 'S', T: str = 'T'
) -> dict:
    functional_q: str = replace_map(
        (
            "Consider a nonempty collection $\\mathcal{P}$ of subsets of $\\{1,\\dots, n\\}$ such that: \\begin{enumerate} "
            "\\item[(i)] if ${S}, {S}' \\in \\mathcal{P}$, then both ${S} \\cup {S}'$ and ${S} \\cap {S}'$ are in $\\mathcal{P}$, "
            "and \\item[(ii)] if ${S} \\in \\mathcal{P}$ and ${S} \\neq \\emptyset$, then there exists a subset ${T} \\subset {S}$ "
            "such that ${T} \\in \\mathcal{P}$ and ${T}$ has exactly one element less than ${S}. \\end{enumerate} Suppose there is "
            "a function ${f}: \\mathcal{P} \\to \\mathbb{R}$ with ${f}(\\emptyset) = 0$ and \\[ {f}({S} \\cup {S}') = {f}({S}) + {f}({S}') - {f}({S} \\cap {S}') \\] "
            "for all ${S},{S}' \\in \\mathcal{P}$. Is it necessarily true that there exist real numbers ${f}_1,\\dots,{f}_n$ such that "
            "\\[ {f}({S}) = \\sum_{i \\in {S}} {f}_i \\] for every ${S} \\in \\mathcal{P}$? Provide a yes or no answer."
        ),
        {
            '{f}': f, '{S}': S, '{T}': T
        }
    )

    functional_ans: str = replace_map(
        (
            "To define them, we make the following observations.  \\setcounter{lemma}{0} \\begin{lemma} For any $i "
            "\\in \\{1,\\dots,n\\}$, if there exists any ${S} \\in P$ containing $i$, then there exist ${S},"
            "{T} \\in P$ such that ${S}$ is the disjoint union of ${T}$ with $\\{i\\}$. \\end{lemma} \\begin{proof} "
            "Let ${S}$ be an element of $P$ containing $i$ of minimum cardinality. By (ii), there must be a subset "
            "${T} \\subset {S}$ containing $P$ with exactly one fewer element than ${S}$. These sets have the "
            "desired form. \\end{proof}  \\begin{lemma} Suppose ${S}_1, {S}_2, {T}_1, {T}_2 \\in P$ have the property "
            "that for some $i \\in \\{1,\\dots,n\\}$, ${S}_1$ is the disjoint union of ${T}_1$ with $\\{i\\}$ and ${"
            "S}_2$ is the disjoint union of ${T}_2$ with $\\{i\\}$. Then  \\[ {f}({S}_1) - {f}({T}_1) = {f}({S}_2) - "
            "{f}({T}_2). \\] \\end{lemma} \\begin{proof} By (i) we have \\begin{align*} {f}({T}_1 \\cup {T}_2 \\cup "
            "\\{i\\}) &= {f}({S}_1) + {f}({T}_2) - {f}({T}_1 \\cap {T}_2) \\\\ {f}({T}_1 \\cup {T}_2 \\cup \\{i\\}) "
            "&= {f}({T}_1) + {f}({S}_2) - {f}({T}_1 \\cap {T}_2), \\end{align*} from which the claim follows "
            "immediately. \\end{proof}  We now define ${f}_1,\\dots,{f}_n$ as follows. If $i$ does not appear in any "
            "element of $P$, we put ${f}_i = 0$. Otherwise, by Lemma~1, we can find  ${S}, {T} \\in P$ such that ${"
            "S}$ is the disjoint union of ${T}$ with $\\{i\\}$. We then set ${f}_i = {f}({S}) - {f}({T})$; by "
            "Lemma~2, this does not depend on the choice of ${S},{T}$.  To check that ${f}({S}) = \\sum_{i \\in {S}} "
            "{f}_i$ for ${S} \\in P$, note first that $\\emptyset \\in P$ by repeated application of (ii) and that ${"
            "f}(\\emptyset) = 0$ by hypothesis. This provides the base case for an induction on the cardinality of ${"
            "S}$; for any nonempty ${S} \\in P$, we may apply (ii) to find ${T} \\subset {S}$ such that ${S}$ is the "
            "disjoint union of ${T}$ and some singleton set $\\{j\\}$. By construction and the induction hypothesis, "
            "we have ${f}({S}) = {f}({T}) + {f}_j = j + \\sum_{i \\in {T}} {f}_i = \\sum_{i \\in {S}} {f}_i$ as "
            "desired. \\boxed{Yes}, such numbers must exist."
        ),
        {
            '{f}': f, '{S}': S, '{T}': T
        }
    )
    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }


@variation(
    year='2013', id='B6',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'n': generators.RandomVariable('both'),
        's': generators.RandomVariable('both'),
    },
    original_params={
        'n': 'n', 's': 's'
    })
def putnam_2013b6(
        n: str = 'n', s: str = 's'
) -> dict:
    functional_q: str = replace_map(
        (
            "Consider an odd integer ${n} \\geq 1$. Alice and Bob play a game by taking turns, starting with Alice. "
            "The game board consists of ${n}$ spaces arranged in a straight line, all of which are initially empty. "
            "On each turn, a player can choose one of the following actions: \\begin{itemize} \\item place a stone in an empty space, or \\item remove a stone from a nonempty space ${s}$, place a stone in the nearest empty space to the left of ${s}$ (if available), and place a stone in the nearest empty space to the right of ${s}$ (if available). \\end{itemize} A move is only allowed if it results in a position that has not been seen before in the game. The player who cannot make a move loses. "
            "Assuming both players play optimally, what moves can Alice make on her first turn? Given that the spaces are numbered from 1 to ${n}, which space should Alice choose to place or remove a stone?"
        ),
        {
            '{n}': n, '{s}': s
        }
    )

    functional_ans: str = replace_map(
        (
            "We start with some terminology.  %Divide the playing area into the \\emph{left half}, the \\emph{central "
            "%space}, and the \\emph{right half}. By a \\emph{block} of stones, we mean a (possibly empty) sequence "
            "of stones occupying consecutive spaces. By the \\emph{extremal blocks}, we mean the (possibly empty) "
            "maximal blocks adjacent to the left and right ends of the playing area.  We refer to a legal move "
            "consisting of placing a stone in an empty space as a move of \\emph{type 1}, and any other legal move as "
            "being of \\emph{type 2}. For $i=0,\\dots,{n}$, let $P_i$ be the collection of positions containing $i$ "
            "stones. Define the \\emph{end zone} as the union $Z = P_{{n}-1} \\cup P_{n}$. In this language, "
            "we make the following observations. \\begin{itemize} \\item Any move of type 1 from $P_i$ ends in $P_{"
            "i+1}$. \\item Any move of type 2 from $P_{n}$ ends in $P_{{n}-1}$. \\item For $i < {n}$, any move of "
            "type 2 from $P_i$ ends in $P_i \\cup P_{i+1}$. \\item At this point, we see that  the number of stones "
            "cannot decrease until we reach the end zone. \\item For $i < {n}-1$, if we start at a position in $P_i$ "
            "where the extremal blocks have length $a,b$, then the only possible moves to $P_i$ decrease one of $a,"
            "b$ while leaving the other unchanged (because they are separated by at least two empty spaces). In "
            "particular, no repetition is possible within $P_i$, so the number of stones must eventually increase to "
            "$i+1$. \\item From any position in the end zone, the legal moves are precisely to the other positions in "
            "the end zone which have not previously occurred. Consequently, after the first move into the end zone, "
            "the rest of the game consists of enumerating all positions in the end zone in some order. \\item At this "
            "point, we may change the rules without affecting the outcome by eliminating the rule on repetitions and "
            "declaring that the first player to move into the end zone loses (because $\\# Z = {n}+1$ is even). "
            "\\end{itemize}  To determine who wins in each position, number the spaces of the board $1,\\dots,"
            "{n}$ from left to right. Define the \\emph{weight} of a position to be the sum of the labels of the "
            "occupied spaces, reduced modulo ${n}+1$. For any given position outside of the end zone,  for each $s=1,"
            "\\dots,{n}$ there is a unique move that adds $s$ to the weight: if $s$ is empty that a move of type 1 "
            "there does the job. Otherwise, $s$ inhabits a block running from $i+1$ to $j-1$ with $i$ and $j$ empty ("
            "or equal to $0$ or ${n}+1$), so the type 2 move at $i+j-s$ (which belongs to the same block) does the "
            "job.  We now verify that a position of weight $s$ outside of the end zone is a win for the player to "
            "move if and only if $s \\neq ({n}+1)/2$. We check this for positions in $P_i$ for $i = n-2, \\dots, "
            "0$ by descending induction. For positions in $P_{{n}-2}$, the only safe moves are in the extremal "
            "blocks; we may thus analyze these positions as two-pile Nim with pile sizes equal to the lengths of the "
            "extremal blocks. In particular, a position is a win for the player to move if and only if the extremal "
            "blocks are unequal, in which case the winning move is to equalize the blocks. In other words, "
            "a position is a win for the player to move unless the empty spaces are at $s$ and ${n}+1-s$ for some $s "
            "\\in \\{1,\\dots,({n}-1)/2\\}$, and indeed these are precisely the positions for which the weight equals "
            "$(1 + \\cdots + {n}) - ({n}+1) \\equiv ({n}+1)/2 \\pmod{{n}+1}$. Given the analysis of positions in $P_{"
            "i+1}$ for some $i$, it is clear that if a position in $P_i$ has weight $s \\neq ({n}+1)/2$, there is a "
            "winning move of weight $t$ where $s+t \\equiv ({n}+1)/2 \\pmod{{n}}$, whereas if $s = ({n}+1)/2$ then no "
            "move leads to a winning position.  It thus follows that the unique winning move for Alice at her first "
            "turn is to move at the central space, as claimed. We show that the only winning first move for Alice "
            "is to place a stone in the central space, i.e., the \\boxed{(n+1)/2} space."
        ),
        {
            '{n}': n, '{s}': s
        }
    )
    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }
