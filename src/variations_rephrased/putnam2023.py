print(__name__)
print(__package__)

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
    year='2023', id='A1',
     generators={  # generators can either be a dictionary of generators or a custom sampling function
        'n': generators.RandomVariable('lower'),
        'x': generators.RandomVariable('lower'),
        'f': generators.RandomVariable('lower'),
        'c_2023': generators.RandomInt(1,100000),
    },
    original_params={
        'n': 'n', 'x': 'x', 'f': 'f', 'c_2023': 2023
    }
)
def putnam_2023a1(
        n: str = 'n', x: str = 'x', f: str = 'f', c_2023: int = 2023
) -> dict:
    '''
    For a positive integer $n$, let $f_n(x) = \\cos(x) \\cos(2x) \\cos(3x) \\cdots \\cos(nx)$. Find the smallest $n$ such that $|f_n''(0)| > 2023$.
    '''
    assert c_2023 > 0, f'Error: c_2023 = {c_2023} must be a positive integer.'

    functional_q: str = replace_map(
        (
            "For a positive integer ${n}$, let ${f}_{n}({x}) = \\cos({x}) \\cos(2{x}) \\cos(3{x}) \\cdots "
            "\\cos({n}{x})$. Find the smallest ${n}$ such that $|{f}_{n}''(0)| > {c_2023}$."
        ),
        {'{n}': n, '{x}': x, '{f}': f, '{c_2023}': c_2023}
    )
    # -- boxed answer
    g = lambda n: n * (n + 1) * (2 * n + 1) // 6
    n_prev = 0
    n_ans = 1
    while g(n_ans) < c_2023:
        n_ans += 1
        n_prev += 1
    c_ans = g(n_ans)
    c_prev = g(n_prev)

    functional_ans: str = replace_map(
        (
            "If we use the product rule to calculate ${f}_{n}\'\'({x})$, the result is a sum of terms of two types: terms where two distinct factors $\\cos(m_1{x})$ and $\\cos(m_2{x})$ have each been differentiated once, and terms where a single factor $\\cos(m{x})$ has been differentiated twice. "
            "When we evaluate at ${x}=0$, all terms of the first type vanish since $\\sin(0)=0$, while the term of the second type involving $(\\cos(m{x}))\'\'$ becomes $-m^2$. Thus \\[ |f_{n}''(0)| = \\left|-\\sum_{m=1}^{n} m^2\\right| = \\frac{{n}({n}+1)(2{n}+1)}{6}. \\] "
            "The function $g({n}) = \\frac{{n}({n}+1)(2{n}+1)}{6}$ is increasing for ${n}\\in\\mathbb{N}$ and satisfies $g({n_prev})={c_prev}$ and $g({n_ans})={c_ans}$. It follows that the answer is ${n}=\\boxed{{n_ans}}$."
        ),
        {'{n}': n, '{x}': x, '{f}': f, '{c_2023}': c_2023, '{n_prev}': n_prev, '{c_prev}': c_prev, '{n_ans}': n_ans,
         '{c_ans}': c_ans}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "constant"
    }


@variation(
    year='2023', id='A2',
    generators = {
        'n' : generators.RandomVariable('lower'),
        'p' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
        'a' : generators.RandomVariable('lower'),
        'k' : generators.RandomVariable('lower'),
        'q' : generators.RandomVariable('lower'),
        'b' : generators.RandomVariable('lower')
    },
    original_params={
        'n': 'n', 'p': 'p', 'x': 'x', 'a': 'a', 'k': 'k', 'q': 'q', 'b': 'b'
    }
)
def putnam_2023a2(
        n: str = 'n', p: str = 'p', x: str = 'x', a: str = 'a', k: str = 'k',
        q: str = 'q', b: str = 'b') -> dict:
    '''
    Let $n$ be an even positive integer. Let $p$ be a monic, real polynomial of degree $2n$; that is to say, $p(x) = x^{2n} + a_{2n-1} x^{2n-1} + \\cdots + a_1 x + a_0$ for some real coefficients $a_0, \\dots, a_{2n-1}$. Suppose that $p(1/k) = k^2$ for all integers $k$ such that $1 \\leq |k| \\leq n$. Find all other real numbers $x$ for which $p(1/x) = x^2$.
    '''

    functional_q: str = replace_map(
        (
            "Let ${n}$ be an even positive integer. Let ${p}$ be a monic, real polynomial of degree $2{n}$; "
            "that is to say, ${p}({x}) = {x}^{2{n}} + {a}_{2{n}-1} {x}^{2{n}-1} + \\cdots + {a}_1 {x} + {a}_0$ for some real coefficients ${a}_0, \\dots, {a}_{2{n}-1}$. "
            "Suppose that ${p}(1/{k}) = {k}^2$ for all integers ${k}$ such that $1 \\leq |{k}| \\leq {n}$. Find all other real numbers ${x}$ for which ${p}(1/{x}) = {x}^2$."
        ),
        {'{n}': n, '{p}': p, '{x}': x, '{a}': a, '{k}': k, '{q}': q, '{b}': b}
    )

    functional_ans: str = replace_map(
        (
            "Define the polynomial ${q}({x}) = {x}^{2{n}+2}-{x}^{2{n}}{p}(1/{x}) = {x}^{2{n}+2}-({a}_0{x}^{2{n}}+\\cdots+{a}_{2{n}-1}{x}+1)$. "
            "The statement that ${p}(1/{x})={x}^2$ is equivalent (for ${x}\\neq 0$) to the statement that ${x}$ is a root of ${q}({x})$. "
            "Thus we know that $\\pm 1,\\pm 2,\\ldots,\\pm {n}$ are roots of ${q}({x})$, and we can write \\[ {q}({x}) = ({x}^2+{a}{x}+{b})({x}^2-1)({x}^2-4)\\cdots ({x}^2-{n}^2) \\] for some monic quadratic polynomial ${x}^2+{a}{x}+{b}$. "
            "Equating the coefficients of ${x}^{2{n}+1}$ and ${x}^0$ on both sides gives $0={a}$ and $-1=(-1)^{n}({n}!)^2 {b}$, respectively. Since ${n}$ is even, we have ${x}^2+{a}{x}+{b} = {x}^2-({n}!)^{-2}$. "
            "We conclude that there are precisely two other real numbers ${x}$ such that ${p}(1/{x})={x}^2$, and they are $\\pm 1/{n}!$. "
            "The only other real numbers with this property are $\\boxed{\\pm 1/{n}!}$. (Note that these are indeed \\emph{other} values than $\\pm 1, \\dots, \\pm {n}$ because ${n}>1$.) "
            
        ),
        {'{n}': n, '{p}': p, '{x}': x, '{a}': a, '{k}': k, '{q}': q, '{b}': b}
    )

    return {
        'problem': functional_q,
        'solution': functional_ans,
        'type' : "variable"
    }


@variation(
    year='2023', id='A3',
    generators = {
        'var_r' : generators.RandomVariable('lower'),
        'fnc_f' : generators.RandomVariable('lower'),
        'fnc_g' : generators.RandomVariable('lower')
    },
    original_params={
        'var_r': 'r', 'fnc_f': 'f', 'fnc_g': 'g'
    }
)
def putnam_2023a3(
        var_r: str = 'r', fnc_f: str = 'f', fnc_g: str = 'g',
) -> dict:
    '''
    Determine the smallest positive real number $r$ such that there exist differentiable functions $f\\colon \\mathbb{R} \\to \\mathbb{R}$ and $g\\colon \\mathbb{R} \\to \\mathbb{R}$ satisfying \\begin{enumerate} \\item[(a)] $f(0) > 0$, \\item[(b)] $g(0) = 0$, \\item[(c)] $|f'(x)| \\leq |g(x)|$ for all $x$, \\item[(d)] $|g'(x)| \\leq |f(x)|$ for all $x$, and \\item[(e)] $f(r) = 0$. \\end{enumerate}
    '''

    # No asserts needed; a simple variable change.

    # -- question
    original_q: str = 'Determine the smallest positive real number $r$ such that there exist differentiable functions $f\\colon \\mathbb{R} \\to \\mathbb{R}$ and $g\\colon \\mathbb{R} \\to \\mathbb{R}$ satisfying \\begin{enumerate} \\item[(a)] $f(0) > 0$, \\item[(b)] $g(0) = 0$, \\item[(c)] $|f\'(x)| \\leq |g(x)|$ for all $x$, \\item[(d)] $|g\'(x)| \\leq |f(x)|$ for all $x$, and \\item[(e)] $f(r) = 0$. \\end{enumerate}'
    functional_q: str = f'''Determine the smallest positive real number ${var_r}$ such that there exist differentiable functions ${fnc_f}\\colon \\mathbb{{R}} \\to \\mathbb{{R}}$ and ${fnc_g}\\colon \\mathbb{{R}} \\to \\mathbb{{R}}$ satisfying \\begin{{enumerate}} \\item[(a)] ${fnc_f}(0) > 0$, \\item[(b)] ${fnc_g}(0) = 0$, \\item[(c)] $|{fnc_f}'(x)| \\leq |{fnc_g}(x)|$ for all $x$, \\item[(d)] $|{fnc_g}'(x)| \\leq |{fnc_f}(x)|$ {fnc_f}o{var_r} all $x$, and \\item[(e)] ${fnc_f}({var_r}) = 0$. \\end{{enumerate}}'''

    original_ans: str = '''The answer is $r=\\boxed{\\frac{\\pi}{2}}$, which manifestly is achieved by setting $f(x)=\\cos x$ and $g(x)=\\sin x$.  \\noindent  Suppose by way of contradiction that there exist some $f,g$ satisfying the stated conditions for some $0 < r<\\frac{\\pi}{2}$. We first note that we can assume that $f(x) \\neq 0$ for $x\\in [0,r)$. Indeed, by continuity, $\\{x\\,|\\,x\\geq 0 \\text{ and } f(x)=0\\}$ is a closed subset of $[0,\\infty)$ and thus has a minimum element $r\'$ with $0<r\'\\leq r$. After replacing $r$ by $r\'$, we now have $f(x)\\neq 0$ for $x\\in [0,r)$.  Next we note that $f(r)=0$ implies $g(r) \\neq 0$. Indeed, define the function $k :\\thinspace \\mathbb{R} \\to \\mathbb{R}$ by $k(x) = f(x)^2+g(x)^2$. Then $|k\'(x)| = 2|f(x)f\'(x)+g(x)g\'(x))| \\leq 4|f(x)g(x)| \\leq 2k(x)$, where the last inequality follows from the AM-GM inequality. It follows that $\\left|\\frac{d}{dx} (\\log k(x))\\right| \\leq 2$ for $x \\in [0,r)$; since $k(x)$ is continuous at $x=r$, we conclude that $k(r) \\neq 0$.  Now define the function $h\\colon [0,r) \\to (-\\pi/2,\\pi/2)$ by $h(x) = \\tan^{-1}(g(x)/f(x))$. We compute that \\[ h\'(x) = \\frac{f(x)g\'(x)-g(x)f\'(x)}{f(x)^2+g(x)^2} \\] and thus \\[ |h\'(x)| \\leq \\frac{|f(x)||g\'(x)|+|g(x)||f\'(x)|}{f(x)^2+g(x)^2} \\leq \\frac{|f(x)|^2+|g(x)|^2}{f(x)^2+g(x)^2} = 1. \\] Since $h(0) = 0$, we have $|h(x)| \\leq x<r$ for all $x\\in [0,r)$. Since $r<\\pi/2$ and $\\tan^{-1}$ is increasing on $(-r,r)$, we conclude that $|g(x)/f(x)|$ is uniformly bounded above by $\\tan r$ for all $x\\in [0,r)$. But this contradicts the fact that $f(r)=0$ and $g(r) \\neq 0$, since $\\lim_{x\\to r^-} g(x)/f(x) = \\infty$. This contradiction shows that $r<\\pi/2$ cannot be achieved.  \\noindent'''
    functional_ans: str = f'''Suppose by way of contradiction that there exist some ${fnc_f},{fnc_g}$ satisfying the stated conditions for some $0 < {var_r}<\\frac{{\\pi}}{{2}}$. We first note that we can assume that ${fnc_f}(x) \\neq 0$ for $x\\in [0,{var_r})$. Indeed, by continuity, $\\{{x\\,|\\,x\\geq 0 \\text{{ and }} {fnc_f}(x)=0\\}}$ is a closed subset of $[0,\\infty)$ and thus has a minimum element ${var_r}'$ with $0<{var_r}'\\leq {var_r}$. After replacing ${var_r}$ by ${var_r}'$, we now have ${fnc_f}(x)\\neq 0$ for $x\\in [0,{var_r})$.  Next we note that ${fnc_f}({var_r})=0$ implies ${fnc_g}({var_r}) \\neq 0$. Indeed, define the function $k :\\thinspace \\mathbb{{R}} \\to \\mathbb{{R}}$ by $k(x) = {fnc_f}(x)^2+{fnc_g}(x)^2$. Then $|k'(x)| = 2|{fnc_f}(x){fnc_f}'(x)+{fnc_g}(x){fnc_g}'(x))| \\leq 4|{fnc_f}(x){fnc_g}(x)| \\leq 2k(x)$, where the last inequality follows from the AM-GM inequality. It follows that $\\left|\\frac{{d}}{{dx}} (\\log k(x))\\right| \\leq 2$ for $x \\in [0,{var_r})$; since $k(x)$ is continuous at $x={var_r}$, we conclude that $k({var_r}) \\neq 0$.  Now define the function $h\\colon [0,{var_r}) \\to (-\\pi/2,\\pi/2)$ by $h(x) = \\tan^{{-1}}({fnc_g}(x)/{fnc_f}(x))$. We compute that \\[ h'(x) = \\frac{{{fnc_f}(x){fnc_g}'(x)-{fnc_g}(x){fnc_f}'(x)}}{{{fnc_f}(x)^2+{fnc_g}(x)^2}} \\] and thus \\[ |h'(x)| \\leq \\frac{{|{fnc_f}(x)||{fnc_g}'(x)|+|{fnc_g}(x)||{fnc_f}'(x)|}}{{{fnc_f}(x)^2+{fnc_g}(x)^2}} \\leq \\frac{{|{fnc_f}(x)|^2+|{fnc_g}(x)|^2}}{{{fnc_f}(x)^2+{fnc_g}(x)^2}} = 1. \\] Since $h(0) = 0$, we have $|h(x)| \\leq x<{var_r}$ for all $x\\in [0,{var_r})$. Since ${var_r}<\\pi/2$ and $\\tan^{{-1}}$ is increasing on $(-{var_r},{var_r})$, we conclude that $|{fnc_g}(x)/{fnc_f}(x)|$ is uniformly bounded above by $\\tan {var_r}$ for all $x\\in [0,{var_r})$. But this contradicts the fact that ${fnc_f}({var_r})=0$ and ${fnc_g}({var_r}) \\neq 0$, since $\\lim_{{x\\to {var_r}^-}} {fnc_g}(x)/{fnc_f}(x) = \\in{fnc_f}ty$. This contradiction shows that ${var_r}<\\pi/2$ cannot be achieved. The answer is ${var_r}=\\boxed{{\\frac{{\\pi}}{{2}}}}$, which manifestly is achieved by setting $f(x)=\\cos x$ and ${fnc_g}(x)=\\sin x$.'''

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


### NEED RANDOM GREEK LETTER???
# @variation(
#     year='2023', id='A4',
#     generators = {
#         'var_v' : generators.RandomVariable('lower'),
#         'var_a' : generators.RandomVariable('lower')
#     },
#     original_params={
#         'var_v': 'v', 'var_a': 'a'
#     }
# )
# def putnam_2023a4(
#         var_v: str = 'v', var_a: str = 'a'
# ) -> dict:
#     '''
#     Let $v_1, \\dots, v_{12}$ be unit vectors in $\\mathbb{R}^3$ from the origin to the vertices of a regular icosahedron. Show that for every vector $v \\in \\mathbb{R}^3$ and every $\\varepsilon > 0$, there exist integers $a_1,\\dots,a_{12}$ such that $\\| a_1 v_1 + \\cdots + a_{12} v_{12} - v \\| < \\varepsilon$.
#     '''
#     ### MAKING THE EXECUTIVE DECISION TO REMOVE THE EPSILON PARAMETER.

#     ### IS POSSIBLE TO VARY TO A TETRAHEDRON OR A CUBE. WILL HAVE TO CHANGE ENTIRE SOLUTION.

#     # -- question
#     var_ep: str = '\\varepsilon',
#     original_q: str = 'Let $v_1, \\dots, v_{12}$ be unit vectors in $\\mathbb{R}^3$ from the origin to the vertices of a regular icosahedron. Show that for every vector $v \\in \\mathbb{R}^3$ and every $\\varepsilon > 0$, there exist integers $a_1,\\dots,a_{12}$ such that $\\| a_1 v_1 + \\cdots + a_{12} v_{12} - v \\| < \\varepsilon$.'
#     functional_q: str = f'''Let ${var_v}_1, \\dots, {var_v}_{{12}}$ be unit vectors in $\\mathbb{{R}}^3$ from the origin to the vertices of a regular icosahedron. Show that for every vector ${var_v} \\in \\mathbb{{R}}^3$ and every ${var_ep} > 0$, there exist integers ${var_a}_1,\\dots,{var_a}_{{12}}$ such that $\\| {var_a}_1 {var_v}_1 + \\cdots + {var_a}_{{12}} {var_v}_{{12}} - {var_v} \\| < {var_ep}$.'''

#     original_ans: str = '''The assumption that all vertices of the icosahedron correspond to vectors of the same length forces the center of the icosahedron to lie at the origin, since the icosahedron is inscribed in a unique sphere. Since scaling the icosahedron does not change whether or not the stated conclusion is true, we may choose coordinates so that the vertices are the cyclic permutations of the vectors $(\\pm \\frac{1}{2}, \\pm \\frac{1}{2} \\phi, 0)$ where $\\phi = \\frac{1+\\sqrt{5}}{2}$ is the golden ratio. The subgroup of $\\RR^3$ generated by these vectors contains $G \\times G \\times G$ where $G$ is the subgroup of $\\RR$ generated by 1 and $\\phi$. Since $\\phi$ is irrational, it generates a dense subgroup of $\\RR/\\ZZ$; hence $G$ is dense in $\\RR$, and so $G \\times G \\times G$ is dense in $\\RR^3$, proving the claim.'''
#     functional_ans: str = f'''The assumption that all vertices of the icosahedron correspond to vectors of the same length forces the center of the icosahedron to lie at the origin, since the icosahedron is inscribed in a unique sphere. Since scaling the icosahedron does not change whether or not the stated conclusion is true, we may choose coordinates so that the vertices are the cyclic permutations of the vectors $(\\pm \\frac{{1}}{{2}}, \\pm \\frac{{1}}{{2}} \\phi, 0)$ where $\\phi = \\frac{{1+\\sqrt{{5}}}}{{2}}$ is the golden ratio. The subgroup of $\\RR^3$ generated by these vectors contains $G \\times G \\times G$ where $G$ is the subgroup of $\\RR$ generated by 1 and $\\phi$. Since $\\phi$ is irrational, it generates a dense subgroup of $\\RR/\\ZZ$; hence $G$ is dense in $\\RR$, and so $G \\times G \\times G$ is dense in $\\RR^3$, proving the claim.'''

#     return {
#         'problem' : functional_q,
#         'solution' : functional_ans,
#         'type' : "variable"
#     }


@variation(
    year='2023', id='A5',
    generators = {
        'fn_f' : generators.RandomVariable('lower'),
        'var_k' : generators.RandomVariable('lower'),
        'var_z' : generators.RandomVariable('lower'),
        'n' : generators.RandomInt(1,100000)
    },
    original_params={
        'fn_f': 'f', 'var_k': 'k', 'var_z': 'z', 'n': 1010
    }
)
def putnam_2023a5(
        fn_f: str = 'f', var_k: str = 'k', var_z: str = 'z', n: int = 1010
) -> dict:
    assert n > 0, f'Error: n = {n} must be positive.'

    # -- Formulate the questions
    original_q: str = 'For a nonnegative integer $k$, let $f(k)$ be the number of ones in the base 3 representation of $k$. Find all complex numbers $z$ such that \\[ \\sum_{k=0}^{3^{1010}-1} (-2)^{f(k)} (z+k)^{2023} = 0. \\]'
    functional_q: str = f'For a nonnegative integer ${var_k}$, let ${fn_f}({var_k})$ be the number of ones in the base 3 representation of ${var_k}$. Find the sum of all complex numbers ${var_z}$ such that \\[ \\sum_{{{var_k}=0}}^{{3^{{{n}}}-1}} (-2)^{{{fn_f}({var_k})}} ({var_z}+{var_k})^{{{2 * n + 3}}} = 0. \\]'

    # -- Now, make the answer string
    original_ans: str = 'The complex numbers $z$ with this property are \\[ \\boxed{-\\frac{3^{1010}-1}{2} and -\\frac{3^{1010}-1}{2}\\pm\\frac{\\sqrt{9^{1010}-1}}{4}\\,i}. \\]  We begin by noting that for $n \\geq 1$, we have the following equality of polynomials in a parameter $x$: \\[ \\sum_{k=0}^{3^n-1} (-2)^{f(k)} x^k = \\prod_{j=0}^{n-1} (x^{2\\cdot 3^j}-2x^{3^j}+1). \\] This is readily shown by induction on $n$, using the fact that for $0\\leq k\\leq 3^{n-1}-1$, $f(3^{n-1}+k)=f(k)+1$ and $f(2\\cdot 3^{n-1}+k)=f(k)$.  Now define a ``shift'' operator $S$ on polynomials in $z$ by $S(p(z))=p(z+1)$; then we can define $S^m$ for all $m\\in\\mathbb{Z}$ by $S^m(p(z))$, and in particular $S^0=I$ is the identity map. Write \\[ p_n(z) := \\sum_{k=0}^{3^n-1}(-2)^{f(k)}(z+k)^{2n+3} \\] for $n \\geq 1$; it follows that  \\begin{align*} p_n(z) &= \\prod_{j=0}^{n-1}(S^{2\\cdot 3^j}-2S^{3^j}+I) z^{2n+3} \\\\ &= S^{(3^n-1)/2} \\prod_{j=0}^{n-1}(S^{3^j}-2I+S^{-3^j}) z^{2n+3}. \\end{align*} Next observe that for any $\\ell$, the operator $S^\\ell-2I+S^{-\\ell}$ acts on polynomials in $z$ in a way that decreases degree by $2$. More precisely, for $m\\geq 0$, we have \\begin{align*} (S^\\ell-2I+S^{-\\ell})z^m &= (z+\\ell)^m-2z^m+(z-\\ell)^m \\\\ &= 2{m\\choose 2}\\ell^2z^{m-2}+2{m\\choose 4}\\ell^4z^{m-4}+O(z^{m-6}). \\end{align*} We use this general calculation to establish the following: for any $1\\leq i\\leq n$, there is a nonzero constant $C_i$ (depending on $n$ and $i$ but not $z$) such that \\begin{gather} \\nonumber \\prod_{j=1}^{i} (S^{3^{n-j}}-2I+S^{-3^{n-j}}) z^{2n+3} \\\\ \\nonumber = C_i\\left(z^{2n+3-2i}+\\textstyle{\\frac{(2n+3-2i)(n+1-i)}{6}}(\\sum_{j=1}^i 9^{n-j})z^{2n+1-2i}\\right) \\\\ +O(z^{2n-1-2i}). \\label{eq:product} \\end{gather} Proving \\eqref{eq:product} is a straightforward induction on $i$: the induction step applies $S^{3^{n-i-1}}-2I+S^{-3^{n-i-1}}$ to the right hand side of \\eqref{eq:product}, using the general formula for $(S^\\ell-2I+S^{-\\ell})z^m$.  Now setting $i=n$ in \\eqref{eq:product}, we find that for some $C_n$, \\[ \\prod_{j=0}^{n-1}(S^{3^j}-2I+S^{-3^j}) z^{2n+3} = C_n\\left(z^3+\\frac{9^n-1}{16}z\\right). \\] The roots of this polynomial are $0$ and $\\pm \\frac{\\sqrt{9^n-1}}{4} i$, and it follows that the roots of $p_n(z)$ are these three numbers minus $\\frac{3^n-1}{2}$. In particular, when $n=1010$, we find that the roots of $p_{1010}(z)$ are as indicated above.'
    functional_ans: str = f'''We begin by noting that for $n \\geq 1$, we have the following equality of polynomials in a parameter $x$: \\[ \\sum_{{{var_k}=0}}^{{3^n-1}} (-2)^{{{fn_f}({var_k})}} x^{var_k} = \\prod_{{j=0}}^{{n-1}} (x^{{2\\cdot 3^j}}-2x^{{3^j}}+1). \\] This is readily shown by induction on $n$, using the fact that for $0\\leq {var_k}\\leq 3^{{n-1}}-1$, $f(3^{{n-1}}+{var_k})={fn_f}({var_k})+1$ and ${fn_f}(2\\cdot 3^{{n-1}}+{var_k})={fn_f}({var_k})$.  Now define a ``shift'' operator $S$ on polynomials in ${var_z}$ by $S(p({var_z}))=p({var_z}+1)$; then we can define $S^m$ for all $m\\in\\mathbb{{Z}}$ by $S^m(p({var_z}))$, and in particular $S^0=I$ is the identity map. Write \\[ p_n({var_z}) := \\sum_{{{var_k}=0}}^{{3^n-1}}(-2)^{{f({var_k})}}({var_z}+{var_k})^{{2n+3}} \\] for $n \\geq 1$; it follows that  \\begin{{align*}} p_n({var_z}) &= \\prod_{{j=0}}^{{n-1}}(S^{{2\\cdot 3^j}}-2S^{{3^j}}+I) {var_z}^{{2n+3}} \\\\ &= S^{{(3^n-1)/2}} \\prod_{{j=0}}^{{n-1}}(S^{{3^j}}-2I+S^{{-3^j}}) {var_z}^{{2n+3}}. \\end{{align*}} Next observe that for any $\\ell$, the operator $S^\\ell-2I+S^{{-\\ell}}$ acts on polynomials in $z$ in a way that decreases degree by $2$. More precisely, for $m\\geq 0$, we have \\begin{{align*}} (S^\\ell-2I+S^{{-\\ell}}){var_z}^m &= (z+\\ell)^m-2{var_z}^m+({var_z}-\\ell)^m \\\\ &= 2{{m\\choose 2}}\\ell^2{var_z}^{{m-2}}+2{{m\\choose 4}}\\ell^4{var_z}^{{m-4}}+O({var_z}^{{m-6}}). \\end{{align*}} We use this general calculation to establish the following: for any $1\\leq i\\leq n$, there is a nonzero constant $C_i$ (depending on $n$ and $i$ but not ${var_z}$) such that \\begin{{gather}} \\nonumber \\prod_{{j=1}}^{{i}} (S^{{3^{{n-j}}}}-2I+S^{{-3^{{n-j}}}}) z^{{2n+3}} \\\\ \\nonumber = C_i\\left({var_z}^{{2n+3-2i}}+\\textstyle{{\\frac{{(2n+3-2i)(n+1-i)}}{{6}}}}(\\sum_{{j=1}}^i 9^{{n-j}}){var_z}^{{2n+1-2i}}\\right) \\\\ +O({var_z}^{{2n-1-2i}}). \\label{{eq:product}} \\end{{gather}} Proving \\eqref{{eq:product}} is a straightforward induction on $i$: the induction step applies $S^{{3^{{n-i-1}}}}-2I+S^{{-3^{{n-i-1}}}}$ to the right hand side of \\eqref{{eq:product}}, using the general formula for $(S^\\ell-2I+S^{{-\\ell}})z^m$.  Now setting $i=n$ in \\eqref{{eq:product}}, we find that for some $C_n$, \\[ \\prod_{{j=0}}^{{n-1}}(S^{{3^j}}-2I+S^{{-3^j}}) {var_z}^{{2n+3}} = C_n\\left({var_z}^3+\\frac{{9^n-1}}{{16}}{var_z}\\right). \\] The roots of this polynomial are $0$ and $\\pm \\frac{{\\sqrt{{9^n-1}}}}{{4}} i$, and it follows that the roots of $p_n({var_z})$ are these three numbers minus $\\frac{{3^n-1}}{{2}}$. In particular, when $n={n}$, we find that the roots of $p_{{{n}}}(z)$ are as indicated above. The complex numbers ${var_z}$ with this property are \\[ -\\frac{{3^{{{n}}}-1}}{{2}} and -\\frac{{3^{{{n}}}-1}}{{2}}\\pm\\frac{{\\sqrt{{9^{{{n}}}-1}}}}{{4}}\\,i. \\] Thus the required sum of all $z$ is \\boxed{{-\\frac{{3^{{{n+1}}}-3}}{{2}}}}.'''
    # Note: new answers are computed directly in the f string.

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }


@variation(
    year='2023', id='A6',
    generators = {
        'n' : generators.RandomVariable('lower'),
        'k' : generators.RandomVariable('lower')
    },
    original_params={
        'n': 'n', 'k': 'k'
    }
)
def putnam_2023a6(
        n: str = 'n', k: str = 'k'
) -> dict:
    # -- Formulate the questions
    functional_q: str = f'Alice and Bob play a game in which they take turns choosing integers from $1$ to ${n}$. Before any integers are chosen, Bob selects a goal of ``odd\'\' or ``even\'\'. On the first turn, Alice chooses one of the ${n}$ integers. On the second turn, Bob chooses one of the remaining integers. They continue alternately choosing one of the integers that has not yet been chosen, until the ${n}$th turn, which is forced and ends the game. Bob wins if the parity of $\\{{{k}\\colon \\mbox{{the number ${k}$ was chosen on the ${k}$th turn}}\\}}$ matches his goal. Find the sum of all valid values of ${n}$ for which Bob will have a winning strategy?'

    # -- Now, make the answer string
    functional_ans: str = f'''Note that we can interpret the game play as building a permutation of $\\{{1,\\dots,{n}\\}}$, and the number of times an integer ${k}$ is chosen on the ${k}$-th turn is exactly the number of fixed points of this permutation.  For ${n}$ even, Bob selects the goal ``even\'\'. Divide $\\{{1,\\dots,{n}\\}}$ into the pairs $\\{{1,2\\}},\\{{3,4\\}},\\dots$; each time Alice chooses an integer, Bob follows suit with the other integer in the same pair. For each pair $\\{{2{k}-1,2{k}\\}}$, we see that $2{k}-1$ is a fixed point if and only if $2{k}$ is, so the number of fixed points is even.  For ${n}$ odd, Bob selects the goal ``odd\'\'. On the first turn, if Alice chooses 1 or 2, then Bob chooses the other one to transpose into the strategy for ${n}-2$ (with no moves made). We may thus assume hereafter that Alice's first move is some ${k} > 2$, which Bob counters with 2; at this point there is exactly one fixed point.   Thereafter, as long as Alice chooses $j$ on the $j$-th turn (for $j \\geq 3$ odd), either $j+1 < {k}$, in which case Bob can choose $j+1$ to keep the number of fixed points odd; or $j+1={k}$, in which case ${k}$ is even and Bob can choose 1 to transpose into the strategy for  ${n}-{k}$ (with no moves made).  Otherwise, at some odd turn $j$, Alice does not choose $j$. At this point, the number of fixed points is odd, and on each subsequent turn Bob can ensure that neither his own move nor Alice\'s next move does not create a fixed point: on any turn $j$ for Bob, if $j+1$ is available Bob chooses it; otherwise, Bob has at least two choices available, so he can choose a value other than $j$. For all {n}, Bob has a winning strategy thus making the required sum $\\boxed{{{n}({n}+1)/2}}$.'''

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


@variation(
    year='2023', id='B1',
    generators = {
        'var_m' : generators.RandomVariable('lower'),
        'var_n' : generators.RandomVariable('lower'),
        'var_i' : generators.RandomVariable('lower'),
        'var_j' : generators.RandomVariable('lower')
    },
    original_params={
        'var_m': 'm', 'var_n': 'n', 'var_i': 'i', 'var_j': 'j'
    }
)
def putnam_2023b1(
        var_m: str = 'm', var_n: str = 'n', var_i: str = 'i', var_j: str = 'j',
) -> dict:
    '''
    Consider an $m$-by-$n$ grid of unit squares, indexed by $(i,j)$ with $1 \\leq i \\leq m$ and $1 \\leq j \\leq n$. There are $(m-1)(n-1)$ coins, which are initially placed in the squares $(i,j)$ with $1 \\leq i \\leq m-1$ and $1 \\leq j \\leq n-1$. If a coin occupies the square $(i,j)$ with $i \\leq m-1$ and $j \\leq n-1$ and the squares $(i+1,j), (i,j+1)$, and $(i+1,j+1)$ are unoccupied, then a legal move is to slide the coin from $(i,j)$ to $(i+1,j+1)$. How many distinct configurations of coins can be reached starting from the initial configuration by a (possibly empty) sequence of legal moves?
    '''

    # -- question
    original_q: str = 'Consider an $m$-by-$n$ grid of unit squares, indexed by $(i,j)$ with $1 \\leq i \\leq m$ and $1 \\leq j \\leq n$. There are $(m-1)(n-1)$ coins, which are initially placed in the squares $(i,j)$ with $1 \\leq i \\leq m-1$ and $1 \\leq j \\leq n-1$. If a coin occupies the square $(i,j)$ with $i \\leq m-1$ and $j \\leq n-1$ and the squares $(i+1,j), (i,j+1)$, and $(i+1,j+1)$ are unoccupied, then a legal move is to slide the coin from $(i,j)$ to $(i+1,j+1)$. How many distinct configurations of coins can be reached starting from the initial configuration by a (possibly empty) sequence of legal moves?'
    functional_q: str = f'''Consider an ${var_m}$-by-${var_n}$ grid of unit squares, indexed by $({var_i},{var_j})$ with $1 \\leq {var_i} \\leq {var_m}$ and $1 \\leq {var_j} \\leq {var_n}$. There are $({var_m}-1)({var_n}-1)$ coins, which are initially placed in the squares $({var_i},{var_j})$ with $1 \\leq {var_i} \\leq {var_m}-1$ and $1 \\leq {var_j} \\leq {var_n}-1$. If a coin occupies the square $({var_i},{var_j})$ with ${var_i} \\leq {var_m}-1$ and ${var_j} \\leq {var_n}-1$ and the squares $({var_i}+1,{var_j}), ({var_i},{var_j}+1)$, and $({var_i}+1,{var_j}+1)$ are unoccupied, then a legal move is to slide the coin from $({var_i},{var_j})$ to $({var_i}+1,{var_j}+1)$. How many distinct configurations of coins can be reached starting from the initial configuration by a (possibly empty) sequence of legal moves?'''

    original_ans: str = '''The number of such configurations is $\\boxed{\\binom{m+n-2}{m-1}}$.  Initially the unoccupied squares form a path from $(1,n)$ to $(m,1)$ consisting of $m-1$ horizontal steps and $n-1$ vertical steps, and every move preserves this property. This yields an injective map from the set of reachable configurations to the set of paths of this form.  Since the number of such paths is evidently $\\binom{m+n-2}{m-1}$ (as one can arrange the horizontal and vertical steps in any order), it will suffice to show that the map we just wrote down is also surjective; that is, that one can reach any path of this form by a sequence of moves.   This is easiest to see by working backwards. Ending at a given path, if this path is not the initial path, then it contains at least one sequence of squares of the form $(i,j) \\to (i,j-1) \\to (i+1,j-1)$. In this case the square $(i+1,j)$ must be occupied, so we can undo a move by replacing this sequence with  $(i,j) \\to (i+1,j) \\to (i+1,j-1)$.'''
    functional_ans: str = f'''Initially the unoccupied squares form a path from $(1,{var_n})$ to $({var_m},1)$ consisting of ${var_m}-1$ horizontal steps and ${var_n}-1$ vertical steps, and every move preserves this property. This yields an injective map from the set of reachable configurations to the set of paths of this form.  Since the number of such paths is evidently $\\binom{{{var_m}+{var_n}-2}}{{{var_m}-1}}$ (as one can arrange the horizontal and vertical steps in any order), it will suffice to show that the map we just wrote down is also surjective; that is, that one can reach any path of this form by a sequence of moves.   This is easiest to see by working backwards. Ending at a given path, if this path is not the initial path, then it contains at least one sequence of squares of the form $({var_i},{var_j}) \\to ({var_i},{var_j}-1) \\to ({var_i}+1,{var_j}-1)$. In this case the square $({var_i}+1,{var_j})$ must be occupied, so we can undo a move by replacing this sequence with  $({var_i},{var_j}) \\to ({var_i}+1,{var_j}) \\to ({var_i}+1,{var_j}-1)$. The number of such configurations is $\\boxed{{\\binom{{{var_m}+{var_n}-2}}{{{var_m}-1}}}}$.'''

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


@variation(
    year='2023', id='B2',
    generators = {
        'var_k' : generators.RandomVariable('lower'),
        'var_n' : generators.RandomVariable('lower')
    },
    original_params={
        'var_k': 'k', 'var_n': 'n'
    }
)
def putnam_2023b2(
        var_k: str = 'k', var_n: str = 'n'
) -> dict:
    '''
    For each positive integer $n$, let $k(n)$ be the number of ones in the binary representation of $2023 \\cdot n$. What is the minimum value of $k(n)$?
    '''
    # IS POSSIBLE TO VARY c_2023. HOWEVER, WILL ALSO HAVE TO DO A MAJOR REWRITE OF THE SOLUTION.

    # -- question
    c_2023 = 2023
    original_q: str = 'For each positive integer $n$, let $k(n)$ be the number of ones in the binary representation of $2023 \\cdot n$. What is the minimum value of $k(n)$?'
    functional_q: str = f'''For each positive integer ${var_n}$, let ${var_k}({var_n})$ be the number of ones in the binary representation of ${c_2023} \\cdot {var_n}$. What is the minimum value of ${var_k}({var_n})$?'''

    original_ans: str = '''The minimum is $\\boxed{3}$.   \\noindent   We record the factorization $2023 = 7\\cdot 17^2$. We first rule out $k(n)=1$ and $k(n)=2$. If $k(n)=1$, then $2023n = 2^a$ for some $a$, which clearly cannot happen. If $k(n)=2$, then $2023n=2^a+2^b=2^b(1+2^{a-b})$ for some $a>b$. Then $1+2^{a-b} \\equiv 0\\pmod{7}$; but $-1$ is not a power of $2$ mod $7$ since every power of $2$ is congruent to either $1$, $2$, or $4 \\pmod{7}$.  We now show that there is an $n$ such that $k(n)=3$. It suffices to find $a>b>0$ such that $2023$ divides $2^a+2^b+1$. First note that $2^2+2^1+1=7$ and $2^3 \\equiv 1 \\pmod{7}$; thus if $a \\equiv 2\\pmod{3}$ and $b\\equiv 1\\pmod{3}$ then $7$ divides $2^a+2^b+1$. Next, $2^8+2^5+1 = 17^2$ and $2^{16\\cdot 17} \\equiv 1 \\pmod{17^2}$ by Euler's Theorem; thus if $a \\equiv 8 \\pmod{16\\cdot 17}$ and $b\\equiv 5 \\pmod{16\\cdot 17}$ then $17^2$ divides $2^a+2^b+1$.  We have reduced the problem to finding $a,b$ such that $a\\equiv 2\\pmod{3}$, $a\\equiv 8\\pmod{16\\cdot 17}$, $b\\equiv 1\\pmod{3}$, $b\\equiv 5\\pmod{16\\cdot 17}$. But by the Chinese Remainder Theorem, integers $a$ and $b$ solving these equations exist and are unique mod $3\\cdot 16\\cdot 17$. Thus we can find $a,b$ satisfying these congruences; by adding appropriate multiples of $3\\cdot 16\\cdot 17$, we can also ensure that $a>b>1$.  \\noindent'''
    functional_ans: str = f'''We record the factorization ${c_2023} = 7\\cdot 17^2$. We first rule out ${var_k}({var_n})=1$ and ${var_k}({var_n})=2$. If ${var_k}({var_n})=1$, then ${c_2023}{var_n} = 2^a$ for some $a$, which clearly cannot happen. If ${var_k}({var_n})=2$, then ${c_2023}{var_n}=2^a+2^b=2^b(1+2^{{a-b}})$ for some $a>b$. Then $1+2^{{a-b}} \\equiv 0\\pmod{{7}}$; but $-1$ is not a power of $2$ mod $7$ since every power of $2$ is congruent to either $1$, $2$, or $4 \\pmod{{7}}$.  We now show that there is an $n$ such that ${var_k}({var_n})=3$. It suffices to find $a>b>0$ such that ${c_2023}$ divides $2^a+2^b+1$. First note that $2^2+2^1+1=7$ and $2^3 \\equiv 1 \\pmod{{7}}$; thus if $a \\equiv 2\\pmod{{3}}$ and $b\\equiv 1\\pmod{{3}}$ then $7$ divides $2^a+2^b+1$. Next, $2^8+2^5+1 = 17^2$ and $2^{{16\\cdot 17}} \\equiv 1 \\pmod{{17^2}}$ by Euler's Theorem; thus if $a \\equiv 8 \\pmod{{16\\cdot 17}}$ and $b\\equiv 5 \\pmod{{16\\cdot 17}}$ then $17^2$ divides $2^a+2^b+1$.  We have reduced the problem to finding $a,b$ such that $a\\equiv 2\\pmod{{3}}$, $a\\equiv 8\\pmod{{16\\cdot 17}}$, $b\\equiv 1\\pmod{{3}}$, $b\\equiv 5\\pmod{{16\\cdot 17}}$. But by the Chinese Remainder Theorem, integers $a$ and $b$ solving these equations exist and are unique mod $3\\cdot 16\\cdot 17$. Thus we can find $a,b$ satisfying these congruences; by adding appropriate multiples of $3\\cdot 16\\cdot 17$, we can also ensure that $a>b>1$. The minimum is $\\boxed{{3}}$.'''

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


@variation(
    year='2023', id='B3',
    generators = {
        'var_y' : generators.RandomVariable('lower'),
        'var_k' : generators.RandomVariable('lower'),
        'var_X' : generators.RandomVariable('upper'),
        'var_n' : generators.RandomVariable('lower')
    },
    original_params={
        'var_y': 'y', 'var_k': 'k', 'var_X': 'X', 'var_n': 'n'
    }
)

def putnam_2023b3(
        var_y: str = 'y', var_k: str = 'k', var_X: str = 'X', var_n: str = 'n'
) -> dict:
    '''
    A sequence $y_1,y_2,\\dots,y_k$ of real numbers is called \\emph{zigzag} if $k=1$, or if $y_2-y_1, y_3-y_2, \\dots, y_k-y_{k-1}$ are nonzero and alternate in sign. Let $X_1,X_2,\\dots,X_n$ be chosen independently from the uniform distribution on $[0,1]$. Let $a(X_1,X_2,\\dots,X_n)$ be the largest value of $k$ for which there exists an increasing sequence of integers $i_1,i_2,\\dots,i_k$ such that $X_{i_1},X_{i_2},\\dots,X_{i_k}$ is zigzag. Find the expected value of $a(X_1,X_2,\\dots,X_n)$ for $n \\geq 2$.
    '''

    # -- question
    original_q: str = 'A sequence $y_1,y_2,\\dots,y_k$ of real numbers is called \\emph{zigzag} if $k=1$, or if $y_2-y_1, y_3-y_2, \\dots, y_k-y_{k-1}$ are nonzero and alternate in sign. Let $X_1,X_2,\\dots,X_n$ be chosen independently from the uniform distribution on $[0,1]$. Let $a(X_1,X_2,\\dots,X_n)$ be the largest value of $k$ for which there exists an increasing sequence of integers $i_1,i_2,\\dots,i_k$ such that $X_{i_1},X_{i_2},\\dots,X_{i_k}$ is zigzag. Find the expected value of $a(X_1,X_2,\\dots,X_n)$ for $n \\geq 2$.'
    functional_q: str = f'''A sequence ${var_y}_1,{var_y}_2,\\dots,{var_y}_{var_k}$ of real numbers is called \\emph{{zigzag}} if ${var_k}=1$, or if ${var_y}_2-{var_y}_1, {var_y}_3-{var_y}_2, \\dots, {var_y}_{var_k}-{var_y}_{{{var_k}-1}}$ are nonzero and alternate in sign. Let ${var_X}_1,{var_X}_2,\\dots,{var_X}_{var_n}$ be chosen independently from the uniform distribution on $[0,1]$. Let $a({var_X}_1,{var_X}_2,\\dots,{var_X}_{var_n})$ be the largest value of ${var_k}$ for which there exists an increasing sequence of integers $i_1,i_2,\\dots,i_{var_k}$ such that ${var_X}_{{i_1}},{var_X}_{{i_2}},\\dots,{var_X}_{{i_{var_k}}}$ is zigzag. Find the expected value of $a({var_X}_1,{var_X}_2,\\dots,{var_X}_{var_n})$ for ${var_n} \\geq 2$.'''

    # -- solution
    original_ans: str = '''The expected value is $\\boxed{\\frac{2n+2}{3}}$.  Divide the sequence $X_1,\\dots,X_n$ into alternating increasing and decreasing segments, with $N$ segments in all. Note that removing one term cannot increase $N$: if the removed term is interior to some segment then the number remains unchanged, whereas if it separates two segments then one of those decreases in length by 1 (and possibly disappears). From this it follows that $a(X_1,\\dots,X_n) = N+1$: in one direction, the endpoints of the segments form a zigzag of length $N+1$; in the other, for any zigzag $X_{i_1},\\dots, X_{i_m}$, we can view it as a sequence obtained from $X_1,\\dots,X_n$ by removing terms, so its number of segments (which is manifestly $m-1$) cannot exceed $N$.  For $n \\geq 3$, $a(X_1,\\dots,X_n) - a(X_2,\\dots,X_{n})$ is 0 if $X_1, X_2, X_3$ form a monotone sequence and 1 otherwise. Since the six possible orderings of $X_1,X_2,X_3$ are equally likely, \\[ \\mathbf{E}(a(X_1,\\dots,X_n) - a(X_1,\\dots,X_{n-1})) = \\frac{2}{3}. \\] Moreover, we always have $a(X_1, X_2) = 2$ because any sequence of two distinct elements is a zigzag. By linearity of expectation plus induction on $n$, we obtain $\\mathbf{E}(a(X_1,\\dots,X_n)) = \\frac{2n+2}{3}$ as claimed.'''
    functional_ans: str = f'''Divide the sequence ${var_X}_1,\\dots,{var_X}_n$ into alternating increasing and decreasing segments, with $N$ segments in all. Note that removing one term cannot increase $N$: if the removed term is interior to some segment then the number remains unchanged, whereas if it separates two segments then one of those decreases in length by 1 (and possibly disappears). From this it follows that $a({var_X}_1,\\dots,{var_X}_n) = N+1$: in one direction, the endpoints of the segments form a zigzag of length $N+1$; in the other, for any zigzag ${var_X}_{{i_1}},\\dots, {var_X}_{{i_m}}$, we can view it as a sequence obtained from ${var_X}_1,\\dots,{var_X}_n$ by removing terms, so its number of segments (which is manifestly $m-1$) cannot exceed $N$.  For $n \\geq 3$, $a({var_X}_1,\\dots,{var_X}_n) - a({var_X}_2,\\dots,{var_X}_{{n}})$ is 0 if ${var_X}_1, {var_X}_2, {var_X}_3$ form a monotone sequence and 1 otherwise. Since the six possible orderings of ${var_X}_1,{var_X}_2,{var_X}_3$ are equally likely, \\[ \\mathbf{{E}}(a({var_X}_1,\\dots,{var_X}_n) - a({var_X}_1,\\dots,{var_X}_{{n-1}})) = \\frac{{2}}{{3}}. \\] Moreover, we always have $a({var_X}_1, {var_X}_2) = 2$ because any sequence of two distinct elements is a zigzag. By linearity of expectation plus induction on $n$, we obtain $\\mathbf{{E}}(a({var_X}_1,\\dots,{var_X}_n)) = \\frac{{2n+2}}{{3}}$ as claimed. The expected value is $\\boxed{{\\frac{{2n+2}}{{3}}}}$.'''

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }


def gen_snapshot_qa_putnam_2023a1(k_num: int = 4, seed: int = 0):
    random.seed(seed)
    # np.random.seed(seed)

    excluded_chars = "nxf"
    for _ in range(k_num):
        n: str = single_char_variable(excluded_chars, 'lower')
        excluded_chars += n
        x: str = single_char_variable(excluded_chars, 'lower')
        excluded_chars += x
        f: str = single_char_variable(excluded_chars, 'lower')
        excluded_chars += f
        c_2023: int = random.randint(1, 100_000)
        original_q, functional_q, original_ans, functional_ans = putnam_2023a1(n, x, f, c_2023)
        add_variation_to_dataset("A1", "", "", functional_q, functional_ans)
        print(functional_q)
        print(functional_ans)


def gen_snapshot_qa_putnam_2023a2(k_num: int = 4, seed: int = 0):
    random.seed(seed)
    # np.random.seed(seed)

    excluded_chars = "npxakqb"
    for k_ in range(k_num):
        n: str = single_char_variable(excluded_chars)
        excluded_chars += n
        p: str = single_char_variable(excluded_chars)
        excluded_chars += p
        x: str = single_char_variable(excluded_chars)
        excluded_chars += x
        a: str = single_char_variable(excluded_chars)
        excluded_chars += a
        k: str = single_char_variable(excluded_chars)
        excluded_chars += k
        q: str = single_char_variable(excluded_chars)
        excluded_chars += q
        b: str = single_char_variable(excluded_chars)
        excluded_chars += b
        original_q, functional_q, original_ans, functional_ans = putnam_2023a2(n, p, x, a, k, q, b)
        add_variation_to_dataset("A2", "", "", functional_q, functional_ans)
        print(functional_q)
        print(functional_ans)
