"""TODO -- teammate 2: propositional CNF encoding.

IMPORTANT: encode() accepts ONLY public state; it must not import engine or
read puzzle files. Use regions.resolve_region for every counting template.
"""
from __future__ import annotations

from models import EncodedKB, PublicState
from regions import resolve_region  # noqa: F401 -- intentional integration point


def encode(public_state: PublicState) -> EncodedKB:
    """Convert revealed clues and known verdicts to CNF.

    Contract:
      - cell_to_var: A1=1, B1=2, ..., A2=size+1, ...
      - positive literal: Criminal, negative: Innocent
      - encode all 6 core clue types and 2 advanced region kinds
      - known_statuses become unit clauses; hidden data NEVER included
      - [] is tautology; [[]] is contradiction
      - set aux_count/num_vars/clause_count precisely

    Suggested direct combinatorial cardinality encoding:
      AT_MOST k: for every (k+1)-subset, clause of negative literals
      AT_LEAST k: for every (n-k+1)-subset, clause of positive literals
      EXACTLY k: concatenate both forms
    """
    raise NotImplementedError("Teammate 2: implement CNF encode(public_state)")
