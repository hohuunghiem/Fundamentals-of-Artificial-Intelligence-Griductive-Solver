from dataclasses import dataclass


@dataclass
class EncodedKB:
    clauses: list            # list[list[int]]
    cell_to_var: dict        # "A1" -> 1, ...
    primary_count: int
    aux_count: int = 0
    num_vars: int = 0
    clause_count: int = 0