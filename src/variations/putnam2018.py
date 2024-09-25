import difflib
import random
import numpy as np
from utils import single_char_variable, replace_map, variation
import os
import json
import math
import generators

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
    year='2018', id='A1',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'a': generators.RandomVariable('lower'),
        'b': generators.RandomVariable('lower'),
    },
    original_params={
        'a': 'a', 'b': 'b'
    }
)

def putnam_2018a1(
        a: str = 'a', b: str = 'b') -> dict:
    functional_q: str = replace_map(
        (
            "Find all ordered pairs $(a,b)$ of positive integers for which \\[ \\frac{1}{{a}} + \\frac{1}{{b}} = \\frac{3}{2018} \\] and determine the ratio of the sum of all a's to the sum of all b's."
        ),
        {'{a}': a, '{b}': b}
    )

    functional_ans: str = replace_map(
        (
            "By clearing denominators and regrouping, we see that the given equation is equivalent to  \\[ (3{a}-2018)(3{b}-2018) = 2018^2. \\] Each of the factors is congruent to $1 \\pmod 3$. "
            " There are $6$ positive factors of $2018^2 = 2^2 \\cdot 1009^2$ that are congruent to $1 \\pmod 3$: $1$, $2^2$, $1009$, $2^2 \\cdot 1009$, $1009^2$, $2^2 \\cdot 1009^2$. "
            "As for negative factors, the ones that are congruent to $1 \\pmod 3$ are $-2, -2 \\cdot 1009, -2 \\cdot 1009^2$. "
            " However, all of these lead to pairs where ${a} \\leq 0$ or ${b} \\leq 0$. These lead to the $6$ possible pairs: $({a},{b}) = (673,1358114)$, $(674,340033)$, $(1009,2018)$, $(2018,1009)$, $(340033,674)$ with the final answer being $\\boxed{344407/1705848}$."
        ),
        {'{a}': a, '{b}': b}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='2018', id='A2',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'S': generators.RandomVariable('upper'),
        'n': generators.RandomVariable('lower'),
        'M': generators.RandomVariable('upper'),
    },
    original_params={
        'S': 'S', 'n': 'n', 'M' : 'M'
    }
)
def putnam_2018a2(
        S: str = 'S', n: str = 'n', M : str = 'M') -> dict:
    functional_q: str = replace_map(
        (
            "Let ${S}_1, {S}_2, \\dots, {S}_{2^{n}-1}$ be the nonempty subsets of $\\{1,2,\\dots,{n}\\}$ in some order, and let ${M}$ be the $(2^{n}-1) \\times (2^{n}-1)$ matrix whose $(i,j)$ entry is" 
            " \\[ m_{ij} = \\begin{cases} 0 & \\mbox{if }{S}_i \\cap {S}_j = \\emptyset; \\\\ 1 & \\mbox{otherwise.} \\end{cases} \\] Calculate the determinant of $M$ and if there are more than one return the sum of all unique determinant values."
        ),
        {'{S}': S, '{n}': n, '{M}' : M}
    )

    functional_ans: str = replace_map(
        (
            "Write ${M}_{n}$ for a $(2^{n}-1) \\times (2^{n}-1)$ matrix of the given form, and note that $\\det {M}_{n}$ does not depend on the ordering of the subsets:" 
            " transposing two subsets has the effect of transposing two rows and then transposing two columns in ${M}_{n}$, and this does not change the determinant.  Clearly $\\det {M}_1 = 1$. We claim that for ${n}>1$," 
            " $\\det {M}_{n} = -(\\det {M}_{{n}-1})^2$, and the desired answer will follow by induction. Let ${S}_1',\\ldots,{S}_{2^{{n}-1}-1}'$ denote the nonempty subsets of $\\{1,\\ldots,{n}-1\\}$ in any order, with resulting matrix ${M}_{{n}-1}$." 
            " Let $m_{ij}'$ denote the $(i,j)$ entry of ${M}_{{n}-1}$. Now order the nonempty subsets ${S}_1,\\ldots,{S}_{2^{n}-1}$ of $\\{1,\\ldots,{n}\\}$ as follows:  \\[ {S}_i= \\begin{cases} {S}_i' &  i \\leq 2^{{n}-1}-1 \\\\ {S}_{i-2^{{n}-1}+1}' \\cup \\{n\\} & 2^{{n}-1} \\leq i \\leq 2^{n}-2 \\\\ \\{n\\} & i=2^{{n}}-1. \\end{cases} \\]" 
            " (For example, if ${S}_1', \\dots, {S}_{2^{{n}-1}-1}'$ are ordered in lexicographic order as binary strings, then so are ${S}_1,\\dots,{S}_{2^{n}-1}$.) Let ${M}_{n}$ be the resulting matrix. Then we have: \\[ {M}_{n} =" 
            " \\left( \\begin{array}{ccc|ccc|c} &&&&&& 0 \\\\ & {M}_{{n}-1} &&& {M}_{{n}-1} && \\vdots \\\\ &&&&&& 0 \\\\ \\hline &&&1 & \\cdots & 1 & 1 \\\\ & {M}_{{n}-1} && \\vdots & \\ddots & \\vdots & \\vdots \\\\ &&&1 &\\cdots & 1 & 1 \\\\ \\hline 0 & \\cdots & 0 & 1 & \\cdots & 1 & 1 \\end{array} \\right). \\]"  
            " In ${M}_{n}$, perform the following operations, which do not change the determinant: subtract the final row from rows $2^{{n}-1}$ through $2^{n}-2$, and then subtract the final column from columns $2^{{n}-1}$ through $2^{n}-2$." 
            " The result is the matrix \\[ \\left( \\begin{array}{ccc|ccc|c} &&&&&& 0 \\\\ & {M}_{{n}-1} &&& {M}_{{n}-1} && \\vdots \\\\ &&&&&& 0 \\\\ \\hline &&&0 & \\cdots & 0 & 0 \\\\ & {M}_{{n}-1} && \\vdots & \\ddots & \\vdots & \\vdots \\\\ &&&0 &\\cdots & 0 & 0 \\\\ \\hline 0 & \\cdots & 0 & 0 & \\cdots & 0 & 1 \\end{array} \\right). \\]"  
            " We can remove the final row and column without changing the determinant. Now swap the first $2^{{n}-1}-1$ rows with the final $2^{{n}-1}-1$ rows: this changes the determinant by an overall factor of $(-1)^{(2^{{n}-1}-1)^2} = -1$. The result is the block-diagonal matrix $\\left( \\begin{matrix} {M}_{{n}-1} & 0 \\\\ {M}_{{n}-1} & {M}_{{n}-1} \\end{matrix} \\right)$," 
            " whose determinant is $(\\det {M}_{{n}-1})^2$. Thus $\\det {M}_{n} = -(\\det {M}_{{n}-1})^2$ as desired. The determinant is $1$ if $n=1$ and $-1$ if $n>1$, making the final answer \\boxed{0}."
        ),
        {'{S}': S, '{n}': n, '{M}' : M}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='2018', id='A3',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'is_cos': generators.RandomInt(0, 1),
        'x': generators.RandomVariable('lower'),
    },
    original_params={
        'is_cos': True, 'x': 'x'
    }
)

def putnam_2018a3(
        is_cos: bool = True, x: str = 'x') -> dict:
    
    greatest = 'greatest'
    maximum = 'maximum'
    maximal = 'maximal'
    maximize = 'maximize'
    cos = 'cos'
    val = '4 \\cos(x_i)^3 - 3 \\cos(x_i)'
    op = '<'
    antiop = '>'
    sign = ''
    antisign = '-'
    if (is_cos != True):
        greatest = 'least'
        maximum = 'minimum'
        maximal = 'minimal'
        maximize = 'minimize'
        cos = 'sin'
        val = '3 \\sin(x_i) - 4 \\sin(x_i)^3'
        op = '>'
        antiop = '<'
        sign = '-'
        antisign = ''

    functional_q: str = replace_map(
        (
            "Determine the {greatest} possible value of $\\sum_{i=1}^{10} \\{cos}(3{x}_i)$ for real numbers ${x}_1,{x}_2,\\dots,{x}_{10}$ satisfying $\\sum_{i=1}^{10} \\{cos}({x}_i) = 0$."
        ),
        {'{greatest}' : greatest, '{maximum}': maximum, '{maximal}': maximal, '{cos}' : cos, '{x}' : x, '{maximize}' : maximize}
    )

    functional_ans: str = replace_map(
        (
             "Since $\\{cos}(3{x}_i) = {val}$, it is equivalent to {maximize} $4 \\sum_{i=1}^{10} y_i^3$ for $y_1,\\dots,y_{10} \\in [-1,1]$ with $\\sum_{i=1}^{10} y_i = 0$;"  
             " note that this domain is compact, so the {maximum} value is guaranteed to exist. For convenience, we establish something slightly stronger: we {maximize} $4 \\sum_{i=1}^{n} y_i^3$ for $y_1,\\dots,y_{n} \\in [-1,1]$ with $\\sum_{i=1}^{n} y_i = 0$," 
             " where $n$ may be any even nonnegative integer up to $10$, and show that the {maximum} is achieved when $n=10$.  We first study the effect of varying $y_i$ and $y_j$ while fixing their sum. If that sum is $s$, then the function $y \\mapsto y^3 + (s-y)^3$" 
             " has constant second derivative $6s$, so it is either everywhere convex or everywhere concave. Consequently, if $(y_1,\\dots,y_{n})$ achieves the {maximum}, then for any two indices $i<j$, at least one of the following must be true: \\begin{itemize} \\item one of $y_i$, $y_j$ is extremal" 
             " (i.e., equal to $1$ or $-1$); \\item $y_i = y_j < 0$ (in which case $s<0$ and the local {maximum} is achieved above); \\item $y_i = -y_j$ (in which case $s=0$ above). \\end{itemize} In the third case, we may discard $y_i$ and $y_j$ and achieve a case with smaller $n$;" 
             " we may thus assume that this does not occur. In this case, all of the non-extremal values are equal to some common value $y {op} 0$, and moreover we cannot have both 1 and -1. We cannot omit {sign}1, as otherwise the condition $\\sum_{i=1}^{n} y_i = 0$ cannot be achieved; we must thus have only the terms {sign}1 and $y$," 
             " occurring with some positive multiplicities $a$ and $b$ adding up to $n$.  Since $a+b=n$ and ${sign}a+by = 0$, we can solve for $y$ to obtain $y = {antisign}a/b$; we then have \\[ 4\\sum_{i=1}^n y_i^3 = {sign}a + by^3 = {sign}4a \\left( 1 - \\frac{a^2}{b^2} \\right). \\] Since $y {antiop} {antisign}1$, we must have $a < b$. For fixed $a$,"
             " the target function increases as $b$ increases, so the optimal case must occur when $a+b=10$. The possible pairs $(a,b)$ at this point are \\[ (1,9), (2,8), (3,7), (4,6); \\] computing the target function for these values yields respectively \\[ {sign}\\frac{32}{9}, {sign}\\frac{15}{2}, {sign}\\frac{480}{49}, {sign}\\frac{80}{9}, \\] yielding ${sign}480/49$ as the {maximum} value. The {maximum} value is $\\boxed{{sign}480/49}$."
        ),
        {'{greatest}' : greatest, '{maximum}': maximum, '{maximal}': maximal, '{cos}' : cos, '{x}' : x, '{val}' : val, '{maximize}' : maximize, '{op}' : op, '{sign}' : sign, '{antisign}' : antisign, '{antiop}' : antiop}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "significant"
    }

@variation(
    year='2018', id='B1',
    generators={
        'a': generators.RandomVariable('lower'),
        'b': generators.RandomVariable('lower'),
        'v' : generators.RandomVariable('lower')
    },
    original_params={
    'a' : 'a', 'b' : 'b', 'v' : 'v'
    }
)

def putnam_2018b1(
        a: str = 'a', b: str = 'b', v: str = 'v') -> dict:

    functional_q : str = replace_map(
       ("Let $\\mathcal{P}$ be the set of vectors defined by \\[ \\mathcal{P} = \\left\\{ \\left. \\begin{pmatrix} {a} \\\\ {b} \\end{pmatrix} \\right| 0 \\leq {a} \\leq 2, 0 \\leq {b} \\leq 100, \\mbox{ and } {a},{b} \\in \\mathbb{Z} \\right\\}. \\]" 
        " Find all $\\mathbf{{v}} \\in \\mathcal{P}$ such that the set $\\mathcal{P} \\setminus \\{ \\mathbf{{v}} \\}$ obtained by omitting vector $\\mathbf{{v}}$ from $\\mathcal{P}$ can be partitioned into two sets of equal size and equal sum." 
        " Compute and return the sum of both coordinates across all vectors you find."),
       {'{a}' : a, '{b}' : b, '{v}' : v}
    )

    functional_ans : str = replace_map(
       ("(For ease of typography, we write tuples instead of column vectors.)  First we show that if $\\mathcal{P} \\setminus \\{\\mathbf{{v}}\\}$ can be partitioned into subsets $S_1$ and $S_2$ of equal size and equal sum, then $\\mathbf{{v}}$ must be of" 
        " the form $(1,{b})$ where ${b}$ is even. For a finite nonempty set $S$ of vectors in $\\mathbb{Z}^2$, let $\\Sigma(S)$ denote the sum of the vectors in $S$.  Since the average $x$- and $y$-coordinates in $\\mathcal{P}$ are $1$ and $50$, respectively," 
        " and there are $3\\cdot 101$ elements in $\\mathcal{P}$, we have \\[ \\Sigma(P) = 303 \\cdot (1,50) = (303,15150).  \\] On the other hand,  \\[ \\Sigma(P) = \\mathbf{{v}}+\\Sigma(S_1)+\\Sigma(S_2) = \\mathbf{{v}}+2\\Sigma(S_1).  \\]" 
        " By parity considerations, the entries of $\\mathbf{{v}}$ must be odd and even, respectively, and thus $\\mathbf{{v}}$ is of the claimed form.  Next suppose $\\mathbf{{v}} = (1,{b})$ where ${b}$ is even. Note that $\\mathcal{P} \\setminus \\{(1,50)\\}$" 
        " can be partitioned into $151$ pairs of (distinct) vectors $(x,y)$ and $(2-x,100-y)$, each summing to $(2,100)$. If ${b} \\neq 50$ then three of these pairs are $\\{(1,{b}),(1,100-{b})\\}$,$\\{(2,{b}),(0,100-{b})\\}$, and $\\{(2,25+{b}/2),(0,75-{b}/2)\\}$." 
        " Of the remaining $148$ pairs, assign half of them to $S_1$ and half to $S_2$, and then complete the partition of $\\mathcal{P} \\setminus \\{\\mathbf{{v}}\\}$ by assigning $(0,100-{b})$, $(2,25+{b}/2)$, and $(1,50)$ to $S_1$ and $(1,100-{b})$, $(2,{b})$, and $(0,75-{b}/2)$ to $S_2$." 
        " (Note that the three vectors assigned to each of $S_1$ and $S_2$ have the same sum $(3,175-{b}/2)$.) By construction, $S_1$ and $S_2$ have the same number of elements, and $\\Sigma(S_1) = \\Sigma(S_2)$.  For ${b}=50$, this construction does not work because $(1,{b}) = (100-{b})$," 
        " but a slight variation can be made.  In this case, three of the pairs in $\\mathcal{P} \\setminus \\{(1,50)\\}$ are $\\{(2,50),(0,50)\\}$, $\\{(1,51),(1,49)\\}$, and $\\{(0,49),(2,51)\\}$. Assign half of the other $148$ pairs to $S_1$ and half to $S_2$, and complete the partition of $\\mathcal{P} \\setminus \\{(1,50)\\}$" 
        " by assigning $(2,50)$, $(1,51)$, and $(0,49)$ to $S_1$ and $(0,50)$, $(1,49)$, and $(2,51)$ to $S_2$. The vectors satisfying this condition are the collection of vectors $(1,{b})$ where $0 \\leq {b} \\leq 100$ and ${b}$ is even, making the final answer \\boxed{2601}."),
       {'{a}' : a, '{b}' : b, '{v}' : v}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(
    year='2018', id='B6',
    generators={
        'S' : generators.RandomVariable('upper'),
        'length' : generators.RandomInt(100, 10000),
        'total_sum' : generators.RandomInt(100, 10000) #NOTE: THIS MUST BE LARGER THAN LEN. HOW DO WE IMPLEMENT THIS RESTRICTION??
    },
    original_params={
        'S' : 'S', 'length' : 2018, 'total_sum' : 1842
    }
)
def putnam_2018b6(
    S: str = 'S', length: int = 2018, total_sum: int = 1842
) -> dict:
    total_sum = total_sum + length ### NOTE: This change forces total_sum to be larger than the length.
    assert length > 0, f'Error: length = {length} must be a positive integer.'
    assert total_sum > length, f'Error: sum = {total_sum} must be greater than length.'

    # -- Formulate the question.
    functional_q: str = f'Let ${S}$ be the set of sequences of length ${length}$ whose terms are in the set $\\{{1,2,3,4,5,6,10\\}}$ and sum to ${total_sum}$. Find the maximum value of the cardinality of $S$.'

    # -- Generate answer string
    functional_ans : str = f'Let $a(k,n)$ denote the number of sequences of length $k$ taken from the set $\\{{1,2,3,4,5,6,10\\}}$ and having sum $n$. We prove that  \\[ a(k,n) < 2^n \\left( \\frac{{2018}}{{2048}} \\right)^k \\] by double induction on $n+k$ and $n-k$.  The claim is clearly true when $n-k \\leq 0$ and in particular when $n=k=1$, the smallest case for $n+k$.  We categorize the sequences counted by $a(k,n)$ by whether they end in $1,2,3,4,5,6,10$; removing the last term of such a sequence yields a sequence counted by $a(k-1,n-1), a(k-1,n-2), a(k-1,n-3), a(k-1,n-4), a(k-1,n-5), a(k-1,n-6), a(k-1,n-10)$, respectively.  Therefore, \\begin{{align*}} a(k,n) &= a(k-1,n-1) + \\cdots \\\\ &\\quad + a(k-1,n-6) + a(k-1,n-10) \\\\ &< (  2^{{n-1}} + \\cdots +   2^{{n-6}}  +  2^{{n-10}} ) \\left( \\frac{{2018}}{{2048}} \\right)^{{k-1}} \\\\ &= 2^n \\left( \\frac{{1}}{{2}} + \\cdots + \\frac{{1}}{{64}} + \\frac{{1}}{{1024}} \\right) \\left( \\frac{{2018}}{{2048}} \\right)^{{k-1}} \\\\ &= 2^n \\left( \\frac{{1009}}{{1024}} \\right) \\left( \\frac{{2018}}{{2048}} \\right)^{{k-1}} \\\\ &= 2^n \\left( \\frac{{2018}}{{2048}} \\right)^{{k}} \\end{{align*}} where we used directly the induction hypothesis to obtain the inequality on the second line. The case $k={length}, n={total_sum}$ yields the desired result with the maximum value being \\boxed{{2^{{{total_sum}}} \\cdot \\left(\\frac{{2018}}{{2048}}\\right)^{{{length}}}}}.'

    # Answer generated inside the f string.
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

# def putnam_2018b6(
#     S: str = 'S', length : int = 2018, totsum : int = 3860
# ) -> dict:

#   assert length > 0, f'Error: length = {length} must be a positive integer.'
#   assert totsum > length, f'Error: totsum = {totsum} must be a positive integer.'

#   # -- Formulate the question.
#   functional_q: str = f'Let ${S}$ be the set of sequences of length ${length}$ whose terms  are in the set $\\{{1,2,3,4,5,6,10\\}}$ and sum to ${totsum}$. Find the maximum value of the cardinality of $S$.'

# #   if debug:
# #     assert original_q == functional_q, f'Error:\n\n {original_q}\n\n {functional_q}\n\n'

#   # -- Generate answer string
#   functional_ans : str = f'Let $a(k,n)$ denote the number of sequences of length $k$ taken from the set $\\{{1,2,3,4,5,6,10\\}}$ and having sum $n$. We prove that  \\[ a(k,n) < 2^n \\left( \\frac{{2018}}{{2048}} \\right)^k \\] by double induction on $n+k$ and $n-k$.  The claim is clearly true when $n-k \\leq 0$ and in particular when $n=k=1$, the smallest case for $n+k$.  We categorize the sequences counted by $a(k,n)$ by whether they end in $1,2,3,4,5,6,10$; removing the last term of such a sequence yields a sequence counted by $a(k-1,n-1), a(k-1,n-2), a(k-1,n-3), a(k-1,n-4), a(k-1,n-5), a(k-1,n-6), a(k-1,n-10)$, respectively.  Therefore, \\begin{{align*}} a(k,n) &= a(k-1,n-1) + \\cdots \\\\ &\\quad + a(k-1,n-6) + a(k-1,n-10) \\\\ &< (  2^{{n-1}} + \\cdots +   2^{{n-6}}  +  2^{{n-10}} ) \\left( \\frac{{2018}}{{2048}} \\right)^{{k-1}} \\\\ &= 2^n \\left( \\frac{{1}}{{2}} + \\cdots + \\frac{{1}}{{64}} + \\frac{{1}}{{1024}} \\right) \\left( \\frac{{2018}}{{2048}} \\right)^{{k-1}} \\\\ &= 2^n \\left( \\frac{{1009}}{{1024}} \\right) \\left( \\frac{{2018}}{{2048}} \\right)^{{k-1}} \\\\ &= 2^n \\left( \\frac{{2018}}{{2048}} \\right)^{{k}} \\end{{align*}} where we used directly the induction hypothesis to obtain the inequality on the second line. The case $k={length}, n={totsum}$ yields the desired result with the maximum value being \\boxed{{2^{{{totsum}}} \\cdot \\left(\\frac{{2018}}{{2048}}\\right)^{{{length}}}}}.'

#   # Answer generated inside the f string.
#   return {
#         'problem' : functional_q,
#         'solution' : functional_ans
#     }


