import difflib
import random
import numpy as np
import math
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
    year='2014', id='A2',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'A': generators.RandomVariable('upper'),
        'n': generators.RandomVariable('lower'),
        'i': generators.RandomVariable('lower'),
        'j': generators.RandomVariable('lower'),
    },
    original_params={
        'A': 'A', 'n': 'n', 'i': 'i', 'j': 'j'
    }
)

def putnam_2014a2(
        A : str = 'A',
        n : str = 'n',
        i : str = 'i',
        j : str = 'j'
) -> dict:

    functional_q: str = replace_map(
        (
            "Let ${A}$ be the ${n} \\times {n}$ matrix whose entry in the ${i}$-th row and ${j}$-th column is" 
            " \\[ \\frac{1}{\\min({i},{j})} \\] for $1 \\leq {i},{j} \\leq {n}$. Compute $\\det({A})$."
        ),
        {'{A}': A, '{n}' : n, '{i}' : i, '{j}' : j}
    )

    functional_ans: str = replace_map(
        (
            "Let $v_1,\\ldots,v_{n}$ denote the rows of ${A}$. The determinant is  unchanged if we replace $v_{n}$ by $v_{n}-v_{{n}-1}$," 
            " and then $v_{{n}-1}$ by  $v_{{n}-1}-v_{{n}-2}$, and so forth, eventually replacing $v_k$ by  $v_k-v_{k-1}$ for $k\\geq 2$." 
            " Since $v_{k-1}$ and $v_k$ agree in their  first $k-1$ entries, and the $k$-th entry of $v_k-v_{k-1}$ is  $\\frac{1}{k} - \\frac{1}{k-1}$," 
            " the result of these row operations is an upper triangular  matrix with diagonal entries $1,\\frac{1}{2}-1,\\frac{1}{3}-\\frac{1}{2},\\ldots,\\frac{1}{{n}}-\\frac{1}{{n}-1}$." 
            " The  determinant is then \\begin{align*} \\prod_{k=2}^{n} \\left( \\frac{1}{k} - \\frac{1}{k-1}\\right) &= \\prod_{k=2}^{n} \\left(\\frac{-1}{k(k-1)} \\right) \\\\ &=  \\boxed{\\frac{(-1)^{{n}-1}}{({n}-1)!{n}!}}. \\end{align*}"
        ),
        {'{A}': A, '{n}' : n, '{i}' : i, '{j}' : j}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }

@variation(
    year='2014', id='A4',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'X': generators.RandomVariable('upper'),
        'x': generators.RandomInt(0, 100_000)
    },
    original_params={
        'X': 'X', 'x': 0
    }
)
def putnam_2014a4(
        X : str = 'X',
        x : int = 0,
) -> dict:
    
    assert x >= 0, f'Error: x = {x} must be a nonnegative integer.'

    functional_q: str = replace_map(
        (
            "Suppose ${X}$ is a random variable that takes on only nonnegative integer values, with $E\\left[ {X} \\right] = 1$, $E\\left[ {X}^2 \\right] = 2$, and $E \\left[ {X}^3 \\right] = 5$." 
            " (Here $E\\left[ y \\right]$ denotes the expectation of the random variable $Y$.) What is the probability that ${X} = {x}$ given the probability that ${X}=0$ reaches a minimum."
        ),
        {'{X}': X, '{x}' : x}
    )

    ans = 0
    if (x == 0) :
        ans = 1/3
    elif (x == 1):
        ans = 1/2
    elif (x == 3):
        ans = 1/6

    functional_ans: str = replace_map(
        (
            "Let $a_n = P({X}=n)$; we want the minimum value for $a_{x}$. If we write  $S_k = \\sum_{n=1}^\\infty n^k a_n$, then the given expectation values  imply that $S_1 = 1$, $S_2 = 2$, $S_3 = 5$." 
            " Now define $f(n) = 11n-6n^2+n^3$, and note that $f(0) = 0$, $f(1)=f(2)=f(3)=6$, and  $f(n)>6$ for $n\\geq 4$; thus $4 = 11S_1-6S_2+S_3 = \\sum_{n=1}^\\infty f(n)a_n \\geq 6 \\sum_{n=1}^{\\infty} a_n$."  
            " Since $\\sum_{n=0}^\\infty a_n = 1$, it  follows that $a_0 \\geq \\frac{1}{3}$. Equality is achieved  when $a_0=\\frac{1}{3}$, $a_1=\\frac{1}{2}$, $a_3=\\frac{1}{6}$, and $a_n = 0$ for all other $n$,  and so the answer is $\\boxed{{ans}}$."
        ),
        {'{X}': X, '{x}' : x, '{ans}' : ans}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }

@variation(
    year='2014', id='B2',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'f': generators.RandomVariable('lower'),
        'x': generators.RandomVariable('lower'),
        'k': generators.RandomInt(1, 100_000)
    },
    original_params={
        'f': 'f', 'x': 'x', 'k': 3
    }
)

def putnam_2014b2(
        f : str = 'f',
        x : str = 'x',
        k : int = 3
) -> dict:
    
    assert k > 1, f'Error: k = {k} must be a positive integer greater than 1.'

    functional_q: str = replace_map(
        (
            "Suppose that ${f}$ is a function on the interval $[1,{k}]$ such that $-1 \\leq {f}({x}) \\leq 1$ for all ${x}$ and $\\int_1^{k} {f}({x})\\,d{x} = 0$." 
            " How large can $\\int_1^{k} \\frac{{f}({x})}{{x}}\\,d{x}$ be?  \\,"
        ),
        {'{f}': f, '{x}' : x, '{k}' : k}
    )

    top = (int) ((k+1)/2)**2
    val = (int) ((k + 1) / 2)

    functional_ans: str = replace_map(
        (
            "In all solutions, we assume that the function ${f}$ is integrable. Let $g({x})$ be $1$ for $1\\leq {x}\\leq {val}$ and $-1$ for ${val}<{x}\\leq {k}$," 
            " and  define $h({x})=g({x})-{f}({x})$. Then $\\int_1^{k} h({x})\\,d{x} = 0$ and $h({x}) \\geq 0$  for $1\\leq {x}\\leq {val}$, $h({x}) \\leq 0$ for ${val}<{x}\\leq {k}$." 
            " Now \\begin{align*} \\int_1^{k} \\frac{h({x})}{{x}}\\,dx & = \\int_1^{val} \\frac{|h({x})|}{{x}}\\,d{x} - \\int_{val}^{k}  \\frac{|h({x})|}{{x}}\\,d{x}\\\\ &\\geq \\int_1^{val} \\frac{|h({x})|}{{val}}\\,d{x} - \\int_{val}^{k} \\frac{|h({x})|}{{val}}\\,d{x} = 0, \\end{align*}" 
            " and thus $\\int_1^{k} \\frac{{f}({x})}{{x}}\\,d{x} \\leq \\int_1^{k} \\frac{g({x})}{{x}}\\,d{x} =  2\\log {val}-\\log {k} = \\log \\frac{{top}}{{k}}$. Since $g({x})$ achieves the upper bound, the answer is $\\boxed{\\log \\frac{{top}}{{k}}}$."
        ),
        {'{f}': f, '{x}' : x, '{k}' : k, '{top}' : top, '{val}' : val}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }

@variation(
    year='2014', id='B5',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'Patniss_bool': generators.RandomInt(0, 1),
        'n': generators.RandomVariable('lower')
    },
    original_params={
        'Patniss_bool': 0, 'n': 'n'
    }
)

def putnam_2014b5(
        Patniss_bool : 0,
        n : str = 'n',
) -> dict:
    
    name1 = "Patniss"
    name2 = "Keeta"
    if (Patniss_bool == 1):
        name1 = "Keeta"
        name2 = "Patness"

    functional_q: str = replace_map(
        (
            "In the 75th annual Putnam Games, participants compete at mathematical games. Patniss and Keeta play a game in which they take turns choosing an element  from the group of invertible ${n} \\times {n}$ matrices with entries in the field $\\mathbb{Z}/p \\mathbb{Z}$ of integers modulo $p$, where ${n}$ is a fixed positive integer and $p$ is a fixed prime number." 
            "The rules of the game are: \\begin{enumerate} \\item[(1)] A player cannot choose an element that has been chosen by either player on any previous turn. \\item[(2)] A player can only choose an element that commutes with all previously chosen elements. \\item[(3)]" 
            "A player who cannot choose an element on his/her turn loses the game. \\end{enumerate} {name1} takes the first turn. Find the minimum value of $p$ for which {name1} wins, for which {name2} wins and compute the product of the two (Your answer may depend on ${n}$ and $p$.)"
        ),
        {'{name1}': name1, '{name2}' : name2, '{n}' : n}
    )

    functional_ans: str = replace_map(
        (
           "We first analyze the analogous game played using an arbitrary finite group $G$. Recall that for any subset $S$ of $G$, the set of elements $g \\in G$ which commute with all elements of $S$ forms a subgroup $Z(S)$ of $G$, called the \\emph{centralizer} (or \\emph{commutant}) of $S$.  At any given point in the game, the set $S$ of previously chosen elements is contained in $Z(S)$." 
           "Initially $S = \\emptyset$ and $Z(S) = G$; after each turn, $S$ is increased by one element and $Z(S)$ is replaced by a subgroup. In particular, if the order of $Z(S)$ is odd at some point, it remains odd thereafter; conversely, if $S$ contains an element of even order, then the order of $Z(S)$ remains even thereafter. Therefore, any element $g \\in G$ for which $Z(\\{g\\})$ has" 
           "odd order is a winning first move for {name1}, while any other first move by {name1} loses if {name2} responds with some $h \\in Z(\\{g\\})$ of even order (e.g., an element of a 2-Sylow subgroup of $Z(\\{g\\})$). In both cases, the win is guaranteed no matter what moves follow.  Now let $G$ be the group of invertible ${n} \\times {n}$ matrices with entries in $\\ZZ/p\\ZZ$." 
           "If $p>2$, then $Z(S)$ will always contain the scalar matrix $-1$ of order 2, so the win for {name2} is guaranteed. (An explicit winning strategy is to answer any move $g$ with the move $-g$.)  If $p=2$, we establish the existence of $g \\in G$ such that $Z(\\{g\\})$ has odd order using the existence of an irreducible polynomial $P(x)$ of degree ${n}$ over $\\ZZ/p\\ZZ$." 
           "We construct an ${n} \\times {n}$ matrix over $\\ZZ/p\\ZZ$ with characteristic polynomial $P(x)$ by taking the \\emph{companion matrix} of $P(x)$: write $P(x) = x^{n} + P_{{n}-1} x^{{n}-1} + \\cdots + P_0$ and set \\[ g = \\begin{pmatrix} 0 & 0 & \\cdots & 0 & -P_0 \\\\ 1 & 0 & \\cdots & 0 & -P_1 \\\\ 0 & 1 & \\cdots & 0 & -P_2 \\\\ \\vdots & \\vdots & \\ddots & \\vdots & \\vdots \\\\ 0 & 0 & \\cdots & 1 & -P_{{n}-1} \\end{pmatrix}. \\]" 
           "In particular, $\\det(g) = (-1)^{n} P_0 \\neq 0$, so $g \\in G$. Over an algebraic closure of $\\ZZ/p \\ZZ$, $g$ becomes diagonalizable with distinct eigenvalues, so any matrix commuting with $g$ must also be diagonalizable, and hence of odd order. In particular, $Z(\\{g\\})$ is of odd order, so {name1} has a winning strategy. We show that {name1} wins if $p=2$ and {name2} wins if $p>2$ (for all ${n}$)" 
           "with the product of the minimum values of $p$ being \\boxed{6}."
        ),
        {'{name1}': name1, '{name2}' : name2, '{n}' : n}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }
