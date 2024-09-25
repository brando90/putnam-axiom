import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
import math
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


@variation(year='2021', id='A1', 
    generators = {
        'n' : generators.RandomInt(0,100000)
    },
    original_params={
    'n' : 2021
})
def putnam_2021a1(
        n : int = 2021) -> dict:
    ''' 
    A grasshopper starts at the origin in the coordinate plane and makes a sequence of hops. Each hop has length $5$, and after each hop the grasshopper is at a point whose coordinates are both integers; thus, there are $12$ possible locations for the grasshopper after the first hop. What is the smallest number of hops needed for the grasshopper to reach the point $(2021, 2021)$?
    '''

    functional_q : str = replace_map(
        ("A grasshopper starts at the origin in the coordinate plane and makes a sequence of hops. Each hop has length $5$, and after each hop the grasshopper is at a point whose coordinates are both integers; thus, there are $12$ possible locations for the grasshopper after the first hop. What is the smallest number of hops needed for the grasshopper to reach the point $({n}, {n})$?"),
        {'{n}' : n}
    )

    # -- boxed answer
    a, b = 0, 0
    while (7 * (a + 1) < n) :
        a += 1
    
    b = math.ceil((n - 7 * a) / 5)

    sum = 2 * a + 2 * b
    sum_minus_one = sum - 1
    two_n = 2 * n

    if a == 1:
        functional_ans : str = replace_map(
            ("Each hop corresponds to adding one of the $12$ vectors $(0,\\pm 5)$, $(\\pm 5,0)$, $(\\pm 3,\\pm 4)$, $(\\pm 4,\\pm 3)$ to the position of the grasshopper. " 
            "Since $({n},{n}) = (3,4)+(4,3)+{b}(0,5)+{b}(5,0)$, the grasshopper can reach $({n},{n})$ in ${a}+{a}+{b}+{b}={sum}$ hops.  "
            "On the other hand, let $z=x+y$ denote the sum of the $x$ and $y$ coordinates of the grasshopper, so that it starts at $z=0$ and ends at $z={two_n}$. "
            "Each hop changes the sum of the $x$ and $y$ coordinates of the grasshopper by at most $7$, and ${two_n} > {sum_minus_one} \\times 7$; "
            "it follows immediately that the grasshopper must take more than ${sum_minus_one}$ hops to get from $(0,0)$ to $({n},{n})$. "
            "The answer is $\\boxed{{sum}}$."),
            {'{n}' : n, '{a}' : a, '{b}' : b, '{sum}' : sum, '{two_n}' : two_n, '{sum_minus_one}' : sum_minus_one}
        )
    elif b == 1:
        functional_ans : str = replace_map(
            ("Each hop corresponds to adding one of the $12$ vectors $(0,\\pm 5)$, $(\\pm 5,0)$, $(\\pm 3,\\pm 4)$, $(\\pm 4,\\pm 3)$ to the position of the grasshopper. " 
            "Since $({n},{n}) = {a}(3,4)+{a}(4,3)+(0,5)+(5,0)$, the grasshopper can reach $({n},{n})$ in ${a}+{a}+{b}+{b}={sum}$ hops.  "
            "On the other hand, let $z=x+y$ denote the sum of the $x$ and $y$ coordinates of the grasshopper, so that it starts at $z=0$ and ends at $z={two_n}$. "
            "Each hop changes the sum of the $x$ and $y$ coordinates of the grasshopper by at most $7$, and ${two_n} > {sum_minus_one} \\times 7$; "
            "it follows immediately that the grasshopper must take more than ${sum_minus_one}$ hops to get from $(0,0)$ to $({n},{n})$. "
            "The answer is $\\boxed{{sum}}$."),
            {'{n}' : n, '{a}' : a, '{b}' : b, '{sum}' : sum, '{two_n}' : two_n, '{sum_minus_one}' : sum_minus_one}
        )
    else:
        functional_ans : str = replace_map(
            ("Each hop corresponds to adding one of the $12$ vectors $(0,\\pm 5)$, $(\\pm 5,0)$, $(\\pm 3,\\pm 4)$, $(\\pm 4,\\pm 3)$ to the position of the grasshopper. " 
            "Since $({n},{n}) = {a}(3,4)+{a}(4,3)+{b}(0,5)+{b}(5,0)$, the grasshopper can reach $({n},{n})$ in ${a}+{a}+{b}+{b}={sum}$ hops.  "
            "On the other hand, let $z=x+y$ denote the sum of the $x$ and $y$ coordinates of the grasshopper, so that it starts at $z=0$ and ends at $z={two_n}$. "
            "Each hop changes the sum of the $x$ and $y$ coordinates of the grasshopper by at most $7$, and ${two_n} > {sum_minus_one} \\times 7$; "
            "it follows immediately that the grasshopper must take more than ${sum_minus_one}$ hops to get from $(0,0)$ to $({n},{n})$. "
            "The answer is $\\boxed{{sum}}$."),
            {'{n}' : n, '{a}' : a, '{b}' : b, '{sum}' : sum, '{two_n}' : two_n, '{sum_minus_one}' : sum_minus_one}
        )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(year='2021', id='A2', 
    generators = {
        'g' : generators.RandomVariable('lower'),
        'x' : generators.RandomVariable('lower'),
        'r' : generators.RandomVariable('lower')
    },
    original_params={
    'g' : 'g', 'x' : 'x', 'r' : 'r'
})
def putnam_2021a2(
        g : str = 'g', x : str = 'x', r : str = 'r') -> dict:
    ''' 
    For every positive real number $x$, let \\[ g(x) = \\lim_{r \\to 0} ((x+1)^{r+1} - x^{r+1})^{\\frac{1}{r}}. \\] Find $\\lim_{x \\to \\infty} \\frac{g(x)}{x}$.
    '''
    functional_q : str = replace_map( 
        ("For every positive real number $x$, let \\[ g(x) = \\lim_{r \\to 0} ((x+1)^{r+1} - x^{r+1})^{\\frac{1}{{r}}}. \\] Find $\\lim_{x \\to \\infty} \\frac{g(x)}{{x}}$."),
        {'{g}' : g, '{x}' : x, '{r}' : r}
    )

    functional_ans : str = replace_map (
        ("By l'H\\^opital's Rule, we have \\begin{align*} &\\lim_{{r}\\to 0} \\frac{\\log(({x}+1)^{{r}+1}-{x}^{{r}+1})}{{r}} \\\\ &\\quad = \\lim_{{r}\\to 0} \\frac{d}{dr} \\log((x+1)^{r+1}-x^{r+1}) \\\\ &\\quad = \\lim_{r\\to 0} \\frac{(x+1)^{r+1}\\log(x+1)-x^{r+1}\\log x}{(x+1)^{r+1}-x^{r+1}} \\\\ &\\quad = (x+1)\\log(x+1)-x\\log x, \\end{align*} where $\\log$ denotes natural logarithm. It follows that $g(x) = e^{(x+1)\\log(x+1)-x\\log x} = \\frac{(x+1)^{x+1}}{x^x}$. Thus \\[ \\lim_{x\\to\\infty} \\frac{g(x)}{{x}} = \\left(\\lim_{x\\to\\infty}\\frac{x+1}{{x}}\\right) \\cdot \\left(\\lim_{x\\to\\infty} \\left(1+\\frac{1}{{x}}\\right)^x\\right) = 1\\cdot e = e. \\]  The limit is $\\boxed{e}$."),
        {'{g}' : g, '{x}' : x, '{r}' : r}
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }

@variation(year='2021', id='A3', 
    generators = {
        'x' : generators.RandomVariable('lower'),
        'y' : generators.RandomVariable('lower'),
        'z' : generators.RandomVariable('lower'),
        'N' : generators.RandomVariable('upper')
    },
    original_params={
    'x' : 'x', 'y' : 'y', 'z' : 'z', 'N' : 'N'
})
def putnam_2021a3(
        x: str = 'x', y: str = 'y', z: str = 'z', N: str = 'N') -> dict:

    functional_q : str = replace_map(
       ("Determine the smallest positive integer ${N}$ for which the sphere \\[ {x}^2 + {y}^2 + {z}^2 = {N} \\] has an inscribed regular tetrahedron whose vertices have integer coordinates."),
       {'{x}' : x, '{y}' : y, '{z}' : z, '{N}' : N}
    )

    functional_ans : str = replace_map(
       ("In one direction, for ${N} = 3{m}^2$, the points \\[ ({m},{m},{m}), ({m},-{m},-{m}), (-{m},{m},-{m}), (-{m},-{m},{m}) \\] form the vertices of a regular tetrahedron inscribed in the sphere" 
        " ${x}^2 + {y}^2 + {z}^2 = {N}$.  Conversely, suppose that $P_i = ({x}_i, {y}_i, {z}_i)$ for $i=1,\\dots,4$ are the vertices of an inscribed regular  tetrahedron." 
        " Then the center of this tetrahedron must equal the center of the sphere, namely $(0,0,0)$. Consequently, these four vertices together with $Q_i = (-{x}_i, -{y}_i, -{z}_i)$ for $i=1,\\dots,4$" 
        " form the vertices of an inscribed cube in the sphere. The side length of this cube is $({N}/3)^{1/2}$, so its volume is $({N}/3)^{3/2}$; on the other hand, this volume also equals the determinant" 
        " of the matrix with row vectors $Q_2-Q_1, Q_3-Q_1, Q_4-Q_1$, which is an integer. Hence $({N}/3)^3$ is a perfect square, as then is ${N}/3$. The integers ${N}$ with this property are those of the form $3{m}^2$" 
        " for some positive integer ${m}$, making the smallest value $\\boxed{3}$."),
       {'{x}' : x, '{y}' : y, '{z}' : z, '{N}' : N, '{m}' : 'm'} 
    )

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
@variation(year='2021', id='A5', 
    generators = {
        'A' : generators.RandomVariable('upper'),
        'n' : generators.RandomVariable('lower'),
        'j' : generators.RandomVariable('lower'),
        'S' : generators.RandomVariable('upper')
    },
    original_params={
    'A' : 'A', 'n' : 'n', 'j' : 'j', 'S' : 'S'
})
def putnam_2021a5(
        A: str = 'A', n : str = 'n', j: str = 'j', S: str = 'S') -> dict:

    functional_q : str = f'Let ${A}$ be the set of all integers $n$ such that $1 \\leq {n} \\leq 2021$ and $\\gcd(n, 2021) = 1$. For every nonnegative integer ${j}$, let \\[ {S}({j}) = \\sum_{{{n} \\in {A}}} {n}^{j}. \\] Determine the maximum value of ${j}$ less than 2021 such that ${S}({j})$ is a multiple of 2021.'

    functional_ans : str = f'We first check that for $p$ prime, \\[ \\sum_{{{n}=1}}^{{p-1}} {n}^{j} \\equiv 0 \\pmod{{p}} \\Leftrightarrow j \\not\\equiv 0 \\pmod{{p-1}}. \\] If ${j} \\equiv 0 \\pmod{{p-1}}$, then ${n}^{j} \\equiv 1 \\pmod{{p}}$ for each ${n}$, so $\\sum_{{{n}=1}}^{{p-1}} {n}^{j} \\equiv p-1 \\pmod{{p}}$. If ${j} \\not\\equiv 0 \\pmod{{p-1}}$, we can pick a primitive root $m$ modulo $p$, observe that $m^{j} \\not\\equiv 1 \\pmod{{p}}$, and then note that \\[ \\sum_{{{n}=1}}^{{p-1}} {n}^{j} \\equiv \\sum_{{{n}=1}}^{{p-1}} (m{n})^{j} = m^{j} \\sum_{{{n}=1}}^{{p-1}} {n}^{j} \\pmod{{p}}, \\] which is only possible if $\\sum_{{{n}=1}}^{{p-1}} {n}^{j} \\equiv 0 \\pmod{{p}}$.  We now note that the prime factorization of 2021 is $43 \\times 47$, so it suffices to determine when ${S}({j})$ is divisible by each of 43 and 47. We have \\begin{{align*}} {S}({j}) &\\equiv 46 \\sum_{{{n}=1}}^{{42}} {n}^{j} \\pmod{{43}} \\\\ {S}({j}) &\\equiv 42 \\sum_{{{n}=1}}^{{46}} {n}^{j} \\pmod{{47}}. \\end{{align*}} Since 46 and 42 are coprime to 43 and 47, respectively,  we have  \\begin{{gather*}} {S}({j}) \\equiv 0 \\pmod{{43}} \\Leftrightarrow {j} \\not\\equiv 0 \\pmod{{42}} \\\\ {S}({j}) \\equiv 0 \\pmod{{47}} \\Leftrightarrow {j} \\not\\equiv 0 \\pmod{{46}}. \\end{{gather*}} This yields the claimed result. The values of ${j}$ in question are those not divisible by either $42$ or $46$, making the maximum value less than 2021, \\boxed{{2020}}.'

    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
@variation(year='2021', id='A6', 
    generators = {
        'P' : generators.RandomVariable('upper'),
        'x' : generators.RandomVariable('lower')
    },
    original_params={
    'P' : 'P', 'x' : 'x'
})
def putnam_2021a6(
        P : str = 'P', x : str = 'x') -> dict:
    ''' 
    Let $P(x)$ be a polynomial whose coefficients are all either $0$ or $1$. Suppose that $P(x)$ can be written as a product of two nonconstant polynomials with integer coefficients. Does it follow that $P(2)$ is a composite integer? Give a yes or no answer.
    '''

    functional_q : str = f'Let ${P}({x})$ be a polynomial whose coefficients are all either $0$ or $1$. Suppose that ${P}({x})$ can be written as a product of two nonconstant polynomials with integer coefficients. Does it follow that ${P}(2)$ is a composite integer? Give a yes or no answer.'
    functional_q : str = f'Let ${P}({x})$ be a polynomial whose coefficients are all either $0$ or $1$. Suppose that ${P}({x})$ can be written as a product of two nonconstant polynomials with integer coefficients. Does it follow that ${P}(2)$ is a composite integer? Give a yes or no answer.'
    functional_ans : str = f'(Note: 1 is neither prime nor composite.)  Write ${P}({x}) = a_0 + a_1 {x} + \\cdots + a_n {x}^n$ with $a_i \\in \\{{0,1\\}}$ and $a_n = 1$. Let $\\alpha$ be an arbitrary root of ${P}$. Since ${P}(\\alpha) = 0$, $\\alpha$ cannot be a positive real number. %In addition, if $\\alpha \\neq 0$ then %\\begin{{align*}} %1 &< |a_{{n-1}} \\alpha^{{-1}} + \\cdots + a_0 \\alpha^{{-n}}| \\\\ %&\\leq |\\alpha|^{{-1}} + \\cdots + |\\alpha|^{{-n}} %\\end{{align*}} %and so $|\\alpha| < 2$. % In addition, if $\\alpha \\neq 0$ then \\begin{{align*}} |1 + a_{{n-1}} \\alpha^{{-1}}| &= |a_{{n-2}} \\alpha^{{-2}} + \\cdots + a_0 \\alpha^{{-n}}| \\\\ &\\leq |\\alpha|^{{-2}} + \\cdots + |\\alpha|^{{-n}}. \\end{{align*}} If $\\alpha \\neq 0$ and $\\mathrm{{Re}}(\\alpha) \\geq 0$, then $\\mathrm{{Re}}(1 + a_{{n-1}} \\alpha^{{-1}}) \\geq 1$ and  \\[ 1 \\leq |\\alpha|^{{-2}} + \\cdots + |\\alpha|^{{-n}} < \\frac{{|\\alpha|^{{-2}}}}{{1 - |\\alpha|^{{-1}}}}; \\] this yields $|\\alpha| < (1 + \\sqrt{{5}})/2$.  By the same token, if $\\alpha \\neq 0$ then \\[ |1 + a_{{n-1}} \\alpha^{{-1}} + a_{{n-2}} \\alpha^{{-2}}| \\leq |\\alpha|^{{-3}} + \\cdots + |\\alpha|^{{-n}}. \\] We deduce from this that $\\mathrm{{Re}}(\\alpha) \\leq 3/2$ as follows. \\begin{{itemize}} \\item There is nothing to check if $\\mathrm{{Re}}(\\alpha) \\leq 0$. \\item If the argument of $\\alpha$ belongs to $[-\\pi/4, \\pi/4]$, then $\\mathrm{{Re}}(\\alpha^{{-1}}), \\mathrm{{Re}}(\\alpha^{{-2}}) \\geq 0$, so \\[ 1 \\leq |\\alpha|^{{-3}} + \\cdots + |\\alpha|^{{-n}} < \\frac{{|\\alpha|^{{-3}}}}{{1 - |\\alpha|^{{-1}}}}. \\] Hence $|\\alpha|^{{-1}}$ is greater than the unique positive root of ${x}^3 + {x} - 1$, which  is greater than $2/3$.  \\item Otherwise, $\\alpha$ has argument in $(-\\pi/2,\\pi/4) \\cup (\\pi/4,\\pi/2)$, so the bound $|\\alpha| < (1 + \\sqrt{{5}})/2$ implies that $\\mathrm{{Re}}(\\alpha) < (1 + \\sqrt{{5}})/(2 \\sqrt{{2}}) < 3/2$. \\end{{itemize}}  By hypothesis, there exists a factorization ${P}({x}) = Q({x})R({x})$ into two nonconstant integer polynomials, which we may assume are monic. $Q({x} + 3/2)$ is a product of polynomials, each of the form ${x} - \\alpha$ where $\\alpha$ is a real root of ${P}$ or of the form \\begin{{align*}} &\\left( {x} + \\frac{{3}}{{2}} - \\alpha\\right) \\left({x} + \\frac{{3}}{{2}} - \\overline{{\\alpha}} \\right) \\\\ &\\quad = {x}^2 + 2 \\mathrm{{Re}}\\left(\\frac{{3}}{{2}} - \\alpha\\right) {x} + \\left|\\frac{{3}}{{2}} - \\alpha \\right|^2 \\end{{align*}} where $\\alpha$ is a nonreal root of ${P}$. It follows that $Q({x}+3/2)$ has positive coefficients; comparing its values at ${x}=1/2$ and ${x}=-1/2$ yields $Q(2) > Q(1)$. We cannot have $Q(1) \\leq 0$, as otherwise the intermediate value theorem would imply that $Q$ has a real root in $[1, \\infty)$; hence $Q(1)  \\geq 1$ and so $Q(2) \\geq 2$. Similarly $R(2) \\geq 2$, so ${P}(2) = Q(2) R(2)$ is composite. \\boxed{{Yes}}, it follows that ${P}(2)$ is a composite integer.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
    
@variation(year='2021', id='B6', 
    generators = {
        'var_N' : generators.RandomVariable('upper'),
        'c_2021' : generators.RandomInt(0,100000),
        'var_X' : generators.RandomVariable('upper')
    },
    original_params={
    'var_N' : 'N', 'c_2021' : 2021, 'var_X' : 'X'
})

def putnam_2021b6(
        var_N : str = 'N', c_2021 : int = 2021, var_X : str = 'X') -> dict:
    ''' 
    Given an ordered list of $3N$ real numbers, we can \\emph{trim} it to form a list of $N$ numbers as follows: We divide the list into $N$ groups of $3$ consecutive numbers, and within each group, discard the highest and lowest numbers, keeping only the median.  Consider generating a random number $X$ by the following procedure: Start with a list of $3^{2021}$ numbers, drawn independently and uniformly at random between 0 and 1. Then trim this list as defined above, leaving a list of $3^{2020}$ numbers. Then trim again repeatedly until just one number remains; let $X$ be this number. Let $\\mu$ be the expected value of $|X - \\frac{1}{2}|$. Show that \\[ \\mu \\geq \\frac{1}{4} \\left( \\frac{2}{3} \\right)^{2021}. \\]  \\end{itemize}  \\end{document}
    '''
    var_mu = '\\mu'

    functional_q = f'Given an ordered list of $3{var_N}$ real numbers, we can \\emph{{trim}} it to form a list of ${var_N}$ numbers as follows: We divide the list into ${var_N}$ groups of $3$ consecutive numbers, and within each group, discard the highest and lowest numbers, keeping only the median.  Consider generating a random number ${var_X}$ by the following procedure: Start with a list of $3^{{{c_2021}}}$ numbers, drawn independently and uniformly at random between 0 and 1. Then trim this list as defined above, leaving a list of $3^{{{c_2021 - 1}}}$ numbers. Then trim again repeatedly until just one number remains; let ${var_X}$ be this number. Let ${var_mu}$ be the expected value of $|{var_X} - \\frac{{1}}{{2}}|$. Find the minimum value of {var_mu}.'
    functional_ans = f'Let $f_k(x)$ be the probability distribution of ${var_X}_k$, the last number remaining when one repeatedly trims a list of $3^k$ random variables chosen with respect to the uniform distribution on $[0,1]$; note that $f_0(x) = 1$ for $x \\in [0,1]$. Let $F_k(x)=\\int_0^x f_k(t)\\,dt$ be the cumulative distribution function; by symmetry, $F_k(\\frac{{1}}{{2}}) = \\frac{{1}}{{2}}$. Let ${var_mu}_k$ be the expected value of ${var_X}_k - \\frac{{1}}{{2}}$; then ${var_mu}_0 = \\frac{{1}}{{4}}$, so it will suffice to prove that ${var_mu}_{{k}} \\geq \\frac{{2}}{{3}} {var_mu}_{{k-1}}$ for $k > 0$.  By integration by parts and symmetry, we have \\[ {var_mu}_k = 2 \\int_0^{{1/2}} \\left( \\frac{{1}}{{2}} - x \\right) f_k(x)\\,dx  = 2 \\int_0^{{1/2}} F_k(x)\\,dx; \\] that is, ${var_mu}_k$ computes twice the area under the curve $y = F_k(x)$ for $0 \\leq x \\leq\\frac{{1}}{{2}}$. Since $F_k$ is a monotone function from $[0, \\frac{{1}}{{2}}]$  with $F_k(0) = 0$ and $F_k(\\frac{{1}}{{2}}) = \\frac{{1}}{{2}}$, we may transpose the axes to obtain \\begin{{equation}} \\label{{eq:2021B6 eq4}} \\mu_k = 2 \\int_0^{{1/2}} \\left( \\frac{{1}}{{2}} - F_k^{{-1}}(y) \\right)\\,dy. \\end{{equation}}  Since $f_k(x)$ is the probability distribution of the median of three random variables chosen with respect to the distribution $f_{{k-1}}(x)$, \\begin{{equation}} \\label{{eq:2021B6 eq1}} f_k(x) = 6 f_{{k-1}}(x) F_{{k-1}}(x) ( 1-F_{{k-1}}(x) ) \\end{{equation}} or equivalently \\begin{{equation}} \\label{{eq:2021B6 eq2}} F_k(x) = 3 F_{{k-1}}(x)^2 - 2 F_{{k-1}}(x)^3. \\end{{equation}} By induction, $F_k$ is the $k$-th iterate of $F_1(x) = 3x^2 -2x^3$, so \\begin{{equation}} \\label{{eq:2021B6 eq5}} F_k(x) = F_{{k-1}}(F_1(x)). \\end{{equation}} Since $f_1(t) = 6t(1-t) \\leq \\frac{{3}}{{2}}$ for $t \\in [0,\\frac{{1}}{{2}}]$, \\[ \\frac{{1}}{{2}} - F_1(x) = \\int_x^{{1/2}} 6t(1-t)\\,dt \\leq \\frac{{3}}{{2}}\\left(\\frac{{1}}{{2}}-x\\right); \\] for $y \\in [0, \\frac{{1}}{{2}}]$, we may take $x = F_{{k}}^{{-1}}(y)$ to obtain \\begin{{equation}} \\label{{eq:2021B6 eq3}} \\frac{{1}}{{2}} - F_k^{{-1}}(y) \\geq \\frac{{2}}{{3}} \\left( \\frac{{1}}{{2}} - F_{{k-1}}^{{-1}}(y) \\right). \\end{{equation}} Using \\eqref{{eq:2021B6 eq5}} and \\eqref{{eq:2021B6 eq3}}, we obtain \\begin{{align*}} {var_mu}_k &= 2 \\int_0^{{1/2}} \\left( \\frac{{1}}{{2}} - F_k^{{-1}}(y) \\right) \\,dy \\\\ &\\geq \\frac{{4}}{{3}} \\int_0^{{1/2}} \\left( \\frac{{1}}{{2}} - F_{{k-1}}^{{-1}}(y) \\right) \\,dy = \\frac{{2}}{{3}}\\mu_{{k-1}} \\end{{align*}} as desired. The minimum value of {var_mu} is \\boxed{{\\frac{{1}}{{4}} \\left( \\frac{{2}}{{3}} \\right)^{{{c_2021}}}}}.'
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }


# # TODO: should this be removed? I had a merge conflict and didn't want to accidentally get rid of this - Kai
# @variation(year='2021', id='A3', original_params={
#     'x' : 'x', 'y' : 'y', 'z' : 'z', 'N' : 'N'
# })
# def putnam_2021a3(
#         x: str = 'x', y: str = 'y', z: str = 'z', N: str = 'N') -> dict:

#     functional_q : str = replace_map(
#        ("Determine the smallest positive integer ${N}$ for which the sphere \\[ {x}^2 + {y}^2 + {z}^2 = {N} \\] has an inscribed regular tetrahedron whose vertices have integer coordinates."),
#        {'{x}' : x, '{y}' : y, '{z}' : z, '{N}' : N}
#     )

#     functional_ans : str = replace_map(
#        ("In one direction, for ${N} = 3{m}^2$, the points \\[ ({m},{m},{m}), ({m},-{m},-{m}), (-{m},{m},-{m}), (-{m},-{m},{m}) \\] form the vertices of a regular tetrahedron inscribed in the sphere" 
#         "${x}^2 + {y}^2 + {z}^2 = {N}$.  Conversely, suppose that $P_i = ({x}_i, {y}_i, {z}_i)$ for $i=1,\\dots,4$ are the vertices of an inscribed regular  tetrahedron." 
#         "Then the center of this tetrahedron must equal the center of the sphere, namely $(0,0,0)$. Consequently, these four vertices together with $Q_i = (-{x}_i, -{y}_i, -{z}_i)$ for $i=1,\\dots,4$" 
#         "form the vertices of an inscribed cube in the sphere. The side length of this cube is $({N}/3)^{1/2}$, so its volume is $({N}/3)^{3/2}$; on the other hand, this volume also equals the determinant" 
#         "of the matrix with row vectors $Q_2-Q_1, Q_3-Q_1, Q_4-Q_1$, which is an integer. Hence $({N}/3)^3$ is a perfect square, as then is ${N}/3$. The integers ${N}$ with this property are those of the form $3{m}^2$" 
#         "for some positive integer ${m}$, making the smallest value $\\boxed{3}$."),
#        {'{x}' : x, '{y}' : y, '{z}' : z, '{N}' : N} 
#     )

#     return {
#         'problem' : functional_q,
#         'solution' : functional_ans
#     }
