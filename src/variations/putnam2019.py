import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators


@variation(
    year='2019', id='A2',
    generators={  # generators can either be a dictionary of generators or a custom sampling function
        'A': generators.RandomVariable('upper'),
        'B': generators.RandomVariable('upper'),
        'C': generators.RandomVariable('upper'),
        'G': generators.RandomVariable('upper'),
        'I': generators.RandomVariable('upper'),
        'alpha': generators.RandomVariable('both'),
        'beta': generators.RandomVariable('both')
    },
    original_params={
        'A': 'A', 'B': 'B', 'C': 'C', 'G': 'G', 'I': 'I', 'alpha': '\\alpha', 'beta': '\\beta', 
    }
)
def putnam_2019a2(
        A: str = 'A', B: str = 'B', C: str = 'C', G: str = 'G', I: str = 'I', alpha: str = '\\alpha', beta: str = '\\beta'
) -> dict:

    functional_q: str = replace_map(
        (
        "In the triangle $\\triangle {A}{B}{C}$, let ${G}$ be the centroid, and let ${I}$ be the center of the inscribed circle. " 
        "Let ${alpha}$ and ${beta}$ be the angles at the vertices ${A}$ and ${B}$, respectively. Suppose that the segment ${I}{G}$ " 
        "is parallel to ${A}{B}$ and that ${beta} = 2 \\tan^{-1} (1/3)$. Find ${alpha}$."
        ),
        {'{A}': A, '{B}': B, '{C}': C, '{G}': G, '{I}': I, '{alpha}': alpha, '{beta}': beta}
    )

    functional_ans: str = replace_map(
        (
            "Let $M$ and $D$ denote the midpoint of ${A}{B}$ and the foot of the altitude from ${C}$ to ${A}{B}$, respectively, and let $r$ be the inradius of $\\bigtriangleup ABC$. Since ${C},{G},M$ are collinear with ${C}M = 3{G}M$, the distance from ${C}$ to line ${A}{B}$ is $3$ times the distance from ${G}$ to ${A}{B}$, and the latter is $r$ since ${I}{G} \\parallel {A}{B}$; hence the altitude ${C}D$ has length $3r$. By the double angle formula for tangent, $\\frac{{C}D}{D{B}} = \\tan{beta} = \\frac{3}{4}$, and so $D{B} = 4r$. Let $E$ be the point where the incircle meets ${A}{B}$; then $E{B} = r/\\tan(\\frac{{beta}}{2}) = 3r$. It follows that $ED = r$, whence the incircle is tangent to the altitude ${C}D$. This implies that $D={A}$, ${A}{B}{C}$ is a right triangle, and ${alpha} = \\boxed{\\frac{\\pi}{2}}$."
        ),
        {'{A}': A, '{B}': B, '{C}': C, '{G}': G, '{I}': I, '{alpha}': alpha, '{beta}': beta}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }

@variation(
    year='2019', id='A4',
    generators={
        'f' : generators.RandomVariable('lower'),
        'S' : generators.RandomVariable('upper'),
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'z' : generators.RandomVariable('lower'),
        'r' : generators.RandomInt(1, 10)
    },
    original_params={
        'f': 'f', 'S' :'S', 'x' :  'x', 'y' : 'y', 'z' : 'z', 'r' : 1
    }
)
def putnam_2019a4(
    f: str = 'f', S : str = 'S', x : str = 'x', y : str = 'y', z : str = 'z', r : int = 1
) -> dict:

    # -- Formulate the question
    #   original_q: str = 'Let $f$ be a continuous real-valued function on $\\mathbb{R}^3$. Suppose that for every sphere $S$ of radius 1, the integral of $f(x,y,z)$ over the surface of $S$ equals 0. Must $f(x,y,z)$ be identically 0?'
    functional_q: str = f'Let ${f}$ be a continuous real-valued function on $\\mathbb{{R}}^3$. Suppose that for every sphere ${S}$ of radius {r}, the integral of ${f}({x},{y},{z})$ over the surface of ${S}$ equals 0. Must ${f}({x},{y},{z})$ be identically 0? Give a yes or no answer.'

    #   if debug:
    #     assert original_q == functional_q, f'Error:\n\n {original_q}\n\n {functional_q}\n\n'
    def multR(r):
        if r == 1:
            return ''
        else:
            return r
    # -- Generate answer string
    #   original_ans: str= '\\noindent \\textbf{Solution 1.} We prove that $\\boxed{(j,k) = (2019, 1010)}$ is a valid solution. More generally, let $p(x)$ be the polynomial of degree $N$ such that $p(2n+1) = F_{2n+1}$ for $0 \\leq n \\leq N$. We will show that $p(2N+3) = F_{2N+3}-F_{N+2}$.   Define a sequence of polynomials $p_0(x),\\ldots,p_N(x)$ by $p_0(x) = p(x)$ and $p_k(x) = p_{k-1}(x)-p_{k-1}(x+2)$ for $k \\geq 1$. Then by induction on $k$, it is the case that $p_k(2n+1) = F_{2n+1+k}$ for $0 \\leq n \\leq N-k$, and also that $p_k$ has degree (at most) $N-k$ for $k \\geq 1$. Thus $p_N(x) = F_{N+1}$ since $p_N(1) = F_{N+1}$ and $p_N$ is constant.   We now claim that for $0\\leq k\\leq N$, $p_{N-k}(2k+3) = \\sum_{j=0}^k F_{N+1+j}$. We prove this again by induction on $k$: for the induction step, we have \\begin{align*} p_{N-k}(2k+3) &= p_{N-k}(2k+1)+p_{N-k+1}(2k+1) \\\\ &= F_{N+1+k}+\\sum_{j=0}^{k-1} F_{N+1+j}. \\end{align*} Thus we have $p(2N+3) = p_0(2N+3) = \\sum_{j=0}^N F_{N+1+j}$.   Now one final induction shows that $\\sum_{j=1}^m F_j = F_{m+2}-1$, and so $p(2N+3) = F_{2N+3}-F_{N+2}$, as claimed. In the case $N=1008$, we thus have $p(2019) = F_{2019} - F_{1010}$.'
    functional_ans : str = f'Let $g :\\thinspace \\mathbb{{R}} \\to \\mathbb{{R}}$ be any continuous function with $g(t+2) = g(t)$ for all $t$ and $\\int_0^2 g(t)\\,dt = 0$ (for instance, $g(t) = \\sin(\\pi t)$). Define ${f}({x},{y},{z}) = g({z})$. We claim that for any sphere ${S}$ of radius ${r}$, $\\iint_{S} {f}\\,d{S} = 0$.   Indeed, let ${S}$ be the sphere with radius ${r}$ centered at $({x}_0,{y}_0,{z}_0)$. We can parametrize ${S}$ by ${S}(\\phi,\\theta) = ({x}_0,{y}_0,{z}_0)+({multR(r)}\\sin\\phi\\cos\\theta, {multR(r)}\\sin\\phi\\sin\\theta, {multR(r)}\\cos\\phi)$ for $\\phi \\in [0,\\pi]$ and $\\theta \\in [0,2\\pi]$. Then we have  \\begin{{align*}} \\iint_{S} {f}({x},{y},{z})\\,d{S} &= \\int_0^\\pi \\int_0^{{2\\pi}} {f}({S}(\\phi,\\theta))\\left\\|\\frac{{\\partial {S}}}{{\\partial \\phi}} \\times \\frac{{\\partial {S}}}{{\\partial \\theta}}\\right\\|\\,d\\theta\\,d\\phi \\\\ &=  \\int_0^\\pi \\int_0^{{2\\pi}} {multR(r**2)} g({z}_0+\\cos\\phi) \\sin\\phi\\,d\\theta\\,d\\phi \\\\ &= 2\\pi \\int_{{-1}}^1 {multR(r**2)} g({z}_0+t)\\,dt, \\end{{align*}}  where we have used the substitution $t = \\cos\\phi$; but this last integral is $0$ for any ${z}_0$ by construction. The answer is \\boxed{{no}}.'

    # Answer generated inside the f string.
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='2019', id='B5',
    generators={
        'var_F': generators.RandomVariable('upper'),
        'var_m' : generators.RandomVariable('lower'),
        'fn_p' : generators.RandomVariable('lower'),
        'deg' : generators.RandomInt(0,100000),
        'var_x' : generators.RandomVariable('lower'),
        'var_n' : generators.RandomVariable('lower'),
        'var_j' : generators.RandomVariable('lower'),
        'var_k' : generators.RandomVariable('lower')
    },
    original_params={
        'var_F': 'F', 'var_m': 'm', 'fn_p':  'p', 'deg': 1008, 'var_x':  'x', 'var_n' : 'n', 'var_j': 'j', 'var_k':  'k'
    }
)
def putnam_2019b5(
    var_F: str ='F', var_m: str = 'm', fn_p: str = 'p', deg: int = 1008, var_x: str = 'x', var_n : str = 'n', var_j: str = 'j', var_k: str = 'k'
) -> dict:
  '''Let $F_m$ be the $m$th Fibonacci number, defined by $F_1 = F_2 = 1$ and $F_m = F_{m-1} + F_{m-2}$ for all $m \\geq 3$.
  Let $p(x)$ be the polynomial of degree $1008$ such that $p(2n+1) = F_{2n+1}$ for $n=0,1,2,\\dots,1008$.
  Find integers $j$ and $k$ such that $p(2019) = F_j - F_k$.'''
  #NOTE: the thing inside of fn_p is 2*deg + 1x

  assert deg > 0, f'Error: n = {deg} must be a positive integer.'

  # -- Formulate the question
#   original_q: str = 'Let $F_m$ be the $m$th Fibonacci number, defined by $F_1 = F_2 = 1$ and $F_m = F_{m-1} + F_{m-2}$ for all $m \\geq 3$. Let $p(x)$ be the polynomial of degree $1008$ such that $p(2n+1) = F_{2n+1}$ for $n=0,1,2,\\dots,1008$. Find integers $j$ and $k$ such that $p(2019) = F_j - F_k$.'
  functional_q: str = f'Let ${var_F}_{var_m}$ be the ${var_m}$th Fibonacci number, defined by ${var_F}_1 = {var_F}_2 = 1$ and ${var_F}_{var_m} = {var_F}_{{{var_m}-1}} + {var_F}_{{{var_m}-2}}$ for all ${var_m} \\geq 3$. Let ${fn_p}({var_x})$ be the polynomial of degree ${deg}$ such that $p(2{var_n}+1) = F_{{2{var_n}+1}}$ for ${var_n}=0,1,2,\\dots,{deg}$. Find integers ${var_j}$ and ${var_k}$ such that $p({2*deg + 3}) = {var_F}_{var_j} - {var_F}_{var_k}$ and give the answer in the form $j/k$.'

#   if debug:
#     assert original_q == functional_q, f'Error:\n\n {original_q}\n\n {functional_q}\n\n'
  
  # -- Generate the boxed answer
  ans_j = 2*deg + 3
  ans_k = deg + 2


  # -- Generate answer string
#   original_ans: str= '\\noindent \\textbf{Solution 1.} We prove that $\\boxed{(j,k) = (2019, 1010)}$ is a valid solution. More generally, let $p(x)$ be the polynomial of degree $N$ such that $p(2n+1) = F_{2n+1}$ for $0 \\leq n \\leq N$. We will show that $p(2N+3) = F_{2N+3}-F_{N+2}$.   Define a sequence of polynomials $p_0(x),\\ldots,p_N(x)$ by $p_0(x) = p(x)$ and $p_k(x) = p_{k-1}(x)-p_{k-1}(x+2)$ for $k \\geq 1$. Then by induction on $k$, it is the case that $p_k(2n+1) = F_{2n+1+k}$ for $0 \\leq n \\leq N-k$, and also that $p_k$ has degree (at most) $N-k$ for $k \\geq 1$. Thus $p_N(x) = F_{N+1}$ since $p_N(1) = F_{N+1}$ and $p_N$ is constant.   We now claim that for $0\\leq k\\leq N$, $p_{N-k}(2k+3) = \\sum_{j=0}^k F_{N+1+j}$. We prove this again by induction on $k$: for the induction step, we have \\begin{align*} p_{N-k}(2k+3) &= p_{N-k}(2k+1)+p_{N-k+1}(2k+1) \\\\ &= F_{N+1+k}+\\sum_{j=0}^{k-1} F_{N+1+j}. \\end{align*} Thus we have $p(2N+3) = p_0(2N+3) = \\sum_{j=0}^N F_{N+1+j}$.   Now one final induction shows that $\\sum_{j=1}^m F_j = F_{m+2}-1$, and so $p(2N+3) = F_{2N+3}-F_{N+2}$, as claimed. In the case $N=1008$, we thus have $p(2019) = F_{2019} - F_{1010}$.'
  functional_ans : str = f'More generally, let ${fn_p}({var_x})$ be the polynomial of degree $N$ such that $p(2{var_n}+1) = {var_F}_{{2{var_n}+1}}$ for $0 \\leq {var_n} \\leq N$. We will show that $p(2N+3) = {var_F}_{{2N+3}}-{var_F}_{{N+2}}$.   Define a sequence of polynomials ${fn_p}_0({var_x}),\\ldots,{fn_p}_N({var_x})$ by ${fn_p}_0({var_x}) = {fn_p}({var_x})$ and ${fn_p}_k({var_x}) = {fn_p}_{{k-1}}({var_x})-{fn_p}_{{k-1}}({var_x}+2)$ for $k \\geq 1$. Then by induction on $k$, it is the case that ${fn_p}_k(2{var_n}+1) = {var_F}_{{2{var_n}+1+k}}$ for $0 \\leq {var_n} \\leq N-k$, and also that ${fn_p}_k$ has degree (at most) $N-k$ for $k \\geq 1$. Thus ${fn_p}_N(x) = {var_F}_{{N+1}}$ since ${fn_p}_N(1) = {var_F}_{{N+1}}$ and ${fn_p}_N$ is constant.   We now claim that for $0\\leq k\\leq N$, ${fn_p}_{{N-k}}(2k+3) = \\sum_{{j=0}}^k {var_F}_{{N+1+j}}$. We prove this again by induction on $k$: for the induction step, we have \\begin{{align*}} {fn_p}_{{N-k}}(2k+3) &= {fn_p}_{{N-k}}(2k+1)+{fn_p}_{{N-k+1}}(2k+1) \\\\ &= {var_F}_{{N+1+k}}+\\sum_{{j=0}}^{{k-1}} {var_F}_{{N+1+j}}. \\end{{align*}} Thus we have ${fn_p}(2N+3) = {fn_p}_0(2N+3) = \\sum_{{j=0}}^N {var_F}_{{N+1+j}}$.   Now one final induction shows that $\\sum_{{j=1}}^m {var_F}_j = {var_F}_{{m+2}}-1$, and so ${fn_p}(2N+3) = {var_F}_{{2N+3}}-{var_F}_{{N+2}}$, as claimed. In the case $N={deg}$, we thus have $p({2*deg + 3}) = F_{{{2*deg+3}}} - F_{{{deg+2}}}$. We thus prove that $({var_j},{var_k}) = ({ans_j}, {ans_k})$ is a valid solution with the final answer thus being $\\boxed{{{ans_j}/{ans_k}}}$.'
#   if debug:
#     assert original_ans == functional_ans, f'Error:\n\n {original_ans}\n\n {functional_ans}\n\n'
  
  return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(
    year='2019', id='B6',
    generators={
        'S': generators.RandomVariable('upper'),
    },
    original_params={
        'S' : 'S',
    }
)
def putnam_2019b6(
        S: str = 'S') -> dict:

    functional_q : str = replace_map(
       ("Let $\\mathbb{Z}^n$ be the integer lattice in $\\mathbb{R}^n$. Two points in $\\mathbb{Z}^n$ are called  \\emph{neighbors} if they differ by exactly $1$ in one coordinate and are equal in all other coordinates."  
        " Find the sum of the first k integers $n \\geq 1$ for which there exist a set of points ${S} \\subset \\mathbb{Z}^n$ satisfying the following two conditions? \\begin{enumerate}" 
        " \\item[(1)] If $p$ is in ${S}$, then none of the neighbors of $p$ is in ${S}$. \\item[(2)] If $p \\in \\mathbb{Z}^n$ is not in ${S}$, then exactly one of the neighbors of $p$ is in ${S}$. \\end{enumerate}"),
       {'{S}' : S}
    )

    functional_ans : str = replace_map(
       ("To construct an example, define the function $f: \\mathbb{Z}^n \\to \\mathbb{Z}/(2n+1) \\mathbb{Z}$ by \\[ f(x_1,\\dots,x_n) = x_1 + 2x_2 + \\cdots + nx_n \\pmod{2n+1}, \\] then let ${S}$ be the preimage of 0."  
        " To check condition (1), note that if $p \\in {S}$ and $q$ is a neighbor of $p$ differing only in coordinate $i$, then \\[ f(q) = f(p) \\pm i \\equiv \\pm i \\pmod{2n+1} \\] and so $q \\notin {S}$."  
        " To check condition (2), note that if $p \\in \\mathbb{Z}^n$ is not in ${S}$, then there exists a unique choice of $i \\in \\{1,\\dots,n\\}$ such that $f(p)$ is congruent to one of $+i$ or $-i$ modulo $2n+1$." 
        " The unique neighbor $q$ of $p$ in ${S}$ is then obtained by either subtracting $1$ from, or adding $1$ to, the $i$-th coordinate of $p$. Such a set exists for every n making the sum of the first k such integers $\\boxed{k(k+1)/2}$."),
       {'{S}' : S}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
