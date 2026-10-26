const problemVariants = [
  {
    kind: "Seed problem",
    title: "Prismoidal volume formula",
    text:
      "A solid is bounded by two bases in the horizontal planes $z = h/2$ and $z = -h/2$, and by such a surface that the area of every section in a horizontal plane is given by a formula of the sort \\[ \\text{Area} = a_0 z^3 + a_1 z^2 + a_2 z + a_3 \\] where some coefficients may be $0$. Find the volume formula where $B_1$ and $B_2$ are the base areas and $M$ is the middle horizontal section.",
    answer: "V = (1/6)h(B_1 + B_2 + 4M)",
  },
  {
    kind: "Variable variation",
    title: "Coordinate and scale substitution",
    text:
      "A solid is bounded by two bases in the horizontal planes $y = r/2$ and $y = -r/2$, and every horizontal section has area \\[ \\text{Area} = a_0 y^3 + a_1 y^2 + a_2 y + a_3. \\] Find the corresponding volume formula using $B_1$, $B_2$, and $M$.",
    answer: "V = (1/6)r(B_1 + B_2 + 4M)",
  },
  {
    kind: "Variable variation",
    title: "Symbolic axis substitution",
    text:
      "A solid is bounded by two bases in the horizontal planes $i = q/2$ and $i = -q/2$, and every horizontal section has area \\[ \\text{Area} = a_0 i^3 + a_1 i^2 + a_2 i + a_3. \\] Find the same prismoidal-style volume formula.",
    answer: "V = (1/6)q(B_1 + B_2 + 4M)",
  },
  {
    kind: "Variable variation",
    title: "Renamed integration direction",
    text:
      "A solid is bounded by two bases in the horizontal planes $q = x/2$ and $q = -x/2$, and every horizontal section has area \\[ \\text{Area} = a_0 q^3 + a_1 q^2 + a_2 q + a_3. \\] Find the volume in terms of $B_1$, $B_2$, and $M$.",
    answer: "V = (1/6)x(B_1 + B_2 + 4M)",
  },
];

const variantButtons = document.querySelectorAll(".tab-button");
const problemKind = document.querySelector("#problem-kind");
const problemTitle = document.querySelector("#problem-title");
const problemText = document.querySelector("#problem-text");
const problemAnswer = document.querySelector("#problem-answer");

function renderVariant(index) {
  const variant = problemVariants[index] || problemVariants[0];
  problemKind.textContent = variant.kind;
  problemTitle.textContent = variant.title;
  problemText.textContent = variant.text;
  problemAnswer.textContent = variant.answer;

  variantButtons.forEach((button) => {
    const isActive = button.dataset.variant === String(index);
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });

  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.typesetPromise([problemText, problemAnswer]).catch(() => {});
  }
}

variantButtons.forEach((button) => {
  button.addEventListener("click", () => {
    renderVariant(Number(button.dataset.variant));
  });
});

document.querySelectorAll(".copy-button").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.querySelector(`#${button.dataset.copyTarget}`);
    if (!target) return;

    const original = button.textContent;
    try {
      await copyText(target.textContent);
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    } catch {
      button.textContent = "Select";
      target.focus?.();
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    }
  });
});

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      // Fall through to the selection-based copy path.
    }
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.top = "-1000px";
  textarea.style.left = "-1000px";
  document.body.append(textarea);
  textarea.select();

  const copied = document.execCommand("copy");
  textarea.remove();

  if (!copied) {
    throw new Error("Copy command failed");
  }
}

renderVariant(0);
