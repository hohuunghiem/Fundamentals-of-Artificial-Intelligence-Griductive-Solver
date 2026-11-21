# Griductive Solver report

This report is adapted from the supplied Bloxorz report template.
It preserves the original HCMUS cover design, blue double border, course header/footer,
typography, spacing, and the five team members with their original student IDs.
The report content structure is changed for Project 2: Griductive Solver.

## Folder layout
Place this `report/` folder beside `Source/` in `~/Lab2/`.

## Copy generated figures
The report expects the ten PNG charts in `figures/`. From `~/Lab2`:

```bash
mkdir -p report/figures
cp Source/experiments/results/figures/*.png report/figures/
```

## Compile
The template uses `fontspec`, so compile with XeLaTeX:

```bash
sudo apt install latexmk texlive-xetex texlive-latex-extra texlive-science -y
cd ~/Lab2/report
latexmk -C
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

## Important
The section files are structured writing drafts with comments. Complete all comments,
verify technical details against the final source code, update the submission date if needed,
and do not submit placeholder text.
