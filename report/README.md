# Griductive Solver report

This report is adapted from the supplied Bloxorz report template.
It preserves the original HCMUS cover design, blue double border, course header/footer,
typography, spacing, and the five team members with their original student IDs.
The report content structure is changed for Project 2: Griductive Solver.

## Project links

- Source code on GitHub — [https://github.com/hohuunghiem/Fundamentals-of-Artificial-Intelligence-Griductive-Solver](https://github.com/hohuunghiem/Fundamentals-of-Artificial-Intelligence-Griductive-Solver)
- Demo video on Google Drive — [https://drive.google.com/file/d/1NBbvhKspHTGH47xaYmq9ht4gE7EEVJkj/view](https://drive.google.com/file/d/1NBbvhKspHTGH47xaYmq9ht4gE7EEVJkj/view)

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

## Reproduce the experiments

Run `python -m experiments.run_experiments` from `Source/` on Linux, for
example Ubuntu or Ubuntu under WSL. The runner uses `SIGALRM` for per-run
timeouts and writes to `Source/experiments/results/`. Run
`python -m experiments.plot_results` from `Source/` to regenerate the charts.
