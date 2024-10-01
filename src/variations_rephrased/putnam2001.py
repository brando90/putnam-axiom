import difflib
import random
import numpy as np
from .utils import single_char_variable, replace_map, variation
import os
import json
from . import generators

@variation(year='2001', id='A4', 
    generators = {
        'area' : generators.RandomInt(1, 100),
    },
    original_params={
    'area' : 1
})
def putnam_2001a4(
    area : int = 1) -> dict:

    functional_q : str = replace_map (
       ("The triangle $ABC$ has an area of {area}.  The three points $E,F,G$ lie, respectively, on sides $BC$, $CA$, $AB$ such that $AE$ bisects $BF$ at point $R$, $BF$ bisects $CG$ at point $S$, and $CG$ bisects $AE$ at point $T$. Compute the area of the triangle $RST$."),
       {'{area}' : area}
    )
    
    if area == 1:
        functional_ans : str = replace_map (
            ("Choose $r,s,t$ so that $EC = rBC, FA = sCA, GB = tCB$, and let $[XYZ]$ denote the area of triangle $XYZ$. Then $[ABE] = [AFE]$ since the triangles have the same altitude and base. Also $[ABE] = (BE/BC) [ABC] = 1-r$, and $[ECF] = (EC/BC)(CF/CA)[ABC] = r(1-s)$ " 
             "(e.g., by the law of sines). Adding this all up yields \\begin{align*} 1 &= [ABE] + [ABF] + [ECF] \\\\ &= 2(1-r) + r(1-s) = 2-r-rs \\end{align*} or $r(1+s) = 1$. Similarly $s(1+t) = t(1+r) = 1$.  Let $f: [0, \\infty) \\to [0, \\infty)$ be the function given by $f(x) = 1/(1+x)$; "
             "then $f(f(f(r))) = r$. However, $f(x)$ is strictly decreasing in $x$, so $f(f(x))$ is increasing and $f(f(f(x)))$ is decreasing. Thus there is at most one $x$ such that $f(f(f(x))) = x$; in fact, since the equation $f(z) = z$ has a positive root $z = (-1 + \\sqrt{5})/2$, we must have $r=s=t=z$.  "
             "We now compute $[ABF] = (AF/AC) [ABC] = z$, $[ABR] = (BR/BF) [ABF] = z/2$, analogously $[BCS] = [CAT] = z/2$, and $[RST] = |[ABC] - [ABR] - [BCS] - [CAT]| = |1 - 3z/2| = \\boxed{\\frac{7 - 3 \\sqrt{5}}{4}}$."),
            {'{area}' : area}
        )
    else :
        functional_ans : str = replace_map (
            ("Choose $r,s,t$ so that $EC = rBC, FA = sCA, GB = tCB$, and let $[XYZ]$ denote the area of triangle $XYZ$. Then $[ABE] = [AFE]$ since the triangles have the same altitude and base. Also $[ABE] = (BE/BC) [ABC] = {area}(1-r)$, and $[ECF] = (EC/BC)(CF/CA)[ABC] = {area}r(1-s)$ " 
             "(e.g., by the law of sines). Adding this all up yields \\begin{align*} {area} &= [ABE] + [ABF] + [ECF] \\\\ &= 2{area}(1-r) + {area}r(1-s) = {area}(2-r-rs) \\end{align*} or $r(1+s) = 1$. Similarly $s(1+t) = t(1+r) = 1$.  Let $f: [0, \\infty) \\to [0, \\infty)$ be the function given by $f(x) = 1/(1+x)$; "
             "then $f(f(f(r))) = r$. However, $f(x)$ is strictly decreasing in $x$, so $f(f(x))$ is increasing and $f(f(f(x)))$ is decreasing. Thus there is at most one $x$ such that $f(f(f(x))) = x$; in fact, since the equation $f(z) = z$ has a positive root $z = (-1 + \\sqrt{5})/2$, we must have $r=s=t=z$.  "
             "We now compute $[ABF] = (AF/AC) [ABC] = {area}z$, $[ABR] = (BR/BF) [ABF] = {area}z/2$, analogously $[BCS] = [CAT] = {area}z/2$, and $[RST] = |[ABC] - [ABR] - [BCS] - [CAT]| = |{area} - 3*{area}z/2| = \\boxed{\\frac{7 - 3*{area} \\sqrt{5}}{4}}$."),
            {'{area}' : area}
        )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }


@variation(year='2001', id='A6', 
    generators = {
        'var_r' : generators.RandomInt(10,100),
        'var_l' : generators.RandomInt(20,40)
    },
    original_params={
    'var_r' : 1, 'var_l' : 4
})
def putnam_2001a6(
    var_r : int = 1, var_l: int = 4
) -> dict:
  assert var_r > 0, f'Error: r = {var_r} must be a positive integer.'
  assert var_l <= 4* var_r, f'Error: the length must be at most 4r = {4 * var_r}.'

  # -- Formulate the questions
  functional_q : str = f'Is it possible for an arc of a parabola within a circle of radius {var_r} to have a length exceeding {var_l}?'

  # -- Now, make the answer string
  functional_ans: str = f'''Consider the arc of the parabola $y=Ax^2$ inside the circle $x^2+(y-{var_r})^2 = {var_r**2}$, where we initially assume that $A > \\frac{{1}}{{{2 * var_r}}}$.  This intersects the circle in three points, $(0,0)$ and $(\\pm \\sqrt{{{2 * var_r}A-1}}/A, ({2 * var_r}A-1)/A)$.  We claim that for $A$ sufficiently large, the length $L$ of the parabolic arc between $(0,0)$ and $(\\sqrt{{{2 * var_r}A-1}}/A, ({2 * var_r}A-1)/A)$ is greater than ${2*var_r}$, which implies the desired result by symmetry.  We express $L$ using the usual formula for arclength: \\begin{{align*}} L &= \\int_0^{{\\sqrt{{{2 * var_r}A-1}}/A}} \\sqrt{{1+(2Ax)^2}} \\, dx \\\\ &= \\frac{{1}}{{2A}} \\int_0^{{2\\sqrt{{{2*var_r}A-1}}}} \\sqrt{{1+x^2}} \\, dx \\\\ &= {2*var_r} + \\frac{{1}}{{2A}} \\left( \\int_0^{{2\\sqrt{{{2*var_r}A-1}}}} (\\sqrt{{1+x^2}}-x)\\,dx -2\\right), \\end{{align*}} where we have artificially introduced $-x$ into the integrand in the last step.  Now, for $x \\geq 0$, \\[ \\sqrt{{1+x^2}}-x = \\frac{{1}}{{\\sqrt{{1+x^2}}+x}} > \\frac{{1}}{{2\\sqrt{{1+x^2}}}} \\geq \\frac{{1}}{{2(x+1)}}; \\] since $\\int_0^\\infty dx/(2(x+1))$ diverges, so does $\\int_0^\\infty (\\sqrt{{1+x^2}}-x)\\,dx$.  Hence, for sufficiently large $A$, we have $\\int_0^{{2\\sqrt{{{2*var_r}A-1}}}} (\\sqrt{{1+x^2}}-x)\\,dx > 2$, and hence $L > {2*var_r}$. The answer is \\boxed{{yes}}.'''


  return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "constant"
    }

@variation(year='2001', id='B6', 
    generators = {
        'a' : generators.RandomVariable('lower'),
        'n' : generators.RandomVariable('lower')
    },
    original_params={
    'a' : 'a', 'n' : 'n'
})
def putnam_2001b6(
    a: str = 'a', n: str = 'n') -> dict:

    functional_q : str = replace_map (
       ("Assume that $({a}_{n})_{{n}\\geq 1}$ is an increasing sequence consisting of positive real numbers with $\\lim {a}_{n}/{n}=0$.  "
        "Is it true that there must exist infinitely many positive integers ${n}$ such that ${a}_{{n}-i}+{a}_{{n}+i}<2{a}_{n}$ for $i=1,2,\\ldots,{n}-1$? Give a yes or no answer."),
       {'{a}' : a, '{n}' : n}
    )

    functional_ans : str = replace_map (
        ("Let $S$ be the convex hull of the set of points $({n}, {a}_{n})$ for ${n} \\geq 0$. Geometrically, $S$ is the intersection of all convex sets (or even all halfplanes) "
         "containing the points $({n}, {a}_{n})$; algebraically, $S$ is the set of points $(x,y)$ which can be written as $c_1({n}_1, {a}_{{n}_1}) + \\cdots + c_k({n}_k, {a}_{{n}_k})$ "
         "for some $c_1, \\dots, c_k$ which are nonnegative of sum 1.  We prove that for infinitely many ${n}$, $({n}, {a}_{n})$ is a vertex on the upper boundary of $S$, and that these ${n}$ satisfy the given condition. "
         "The condition that $({n}, {a}_{n})$ is a vertex on the upper boundary of $S$ is equivalent to the existence of a line passing through $({n}, {a}_{n})$ with all other points of $S$ below it. "
         "That is, there should exist $m>0$ such that \\begin{equation} \\label{eq1} {a}_k < {a}_{n} + m(k-{n}) \\qquad \\forall k \\geq 1. \\end{equation}  We first show that ${n}=1$ satisfies (\\ref{eq1}). "
         "The condition ${a}_k/k \\to 0$ as $k \\to \\infty$ implies that $({a}_k - {a}_1)/(k-1) \\to 0$ as well. Thus the set $\\{({a}_k-{a}_1)/(k-1)\\}$ has an upper bound $m$, and now ${a}_k \\leq {a}_1 + m(k-1)$, as desired.  "
         "Next, we show that given one ${n}$ satisfying (\\ref{eq1}), there exists a larger one also satisfying (\\ref{eq1}). Again, the condition ${a}_k/k \\to 0$ as $k \\to \\infty$ implies that $({a}_k-{a}_{n})/(k-{n}) \\to 0$ as $k \\to \\infty$. "
         "Thus the sequence $\\{({a}_k-{a}_{n})/(k-{n})\\}_{k>{n}}$ has a maximum element; suppose $k = r$ is the largest value that achieves this maximum, and put $m = ({a}_r -{a}_{n})/(r-{n})$. Then the line through $(r, {a}_r)$ of slope $m$ lies strictly above $(k, {a}_k)$ for $k > r$ "
         "and passes through or lies above $(k, {a}_k)$ for $k< r$. Thus (\\ref{eq1}) holds for ${n}=r$ with $m$ replaced by $m-\\epsilon$ for suitably small $\\epsilon > 0$.  By induction, we have that (\\ref{eq1}) holds for infinitely many ${n}$. For any such ${n}$ there exists $m>0$ such that for $i=1, "
         "\\dots, {n}-1$, the points $({n}-i, {a}_{{n}-i})$ and $({n}+i, {a}_{{n}+i})$ lie below the line through $({n}, {a}_{n})$ of slope $m$. That means ${a}_{{n}+i} < {a}_{n} + mi$ and ${a}_{{n}-i} < {a}_{n} - mi$; adding these together gives ${a}_{{n}-i} + {a}_{{n}+i} < 2{a}_{n}$, as desired. \\boxed{Yes}, there must exist infinitely many such ${n}$."),
        {'{a}' : a, '{n}' : n} 
    )
    return {
        'problem' : functional_q,
        'solution' : functional_ans,
        'type' : "variable"
    }
