#!/usr/bin/env python3
"""
Standard Problem Generators
============================

Generates benchmark problem instances for evaluating combinatorial optimization
solvers. All generators use published, standard algorithms.

These generators are NOT proprietary -- they implement well-known problem
construction methods from the optimization literature.

Usage:
    python scripts/generate_problems.py ising --n 1000 --seed 42
    python scripts/generate_problems.py sat --n 1000 --alpha 4.27 --seed 42
    python scripts/generate_problems.py maxcut --n 1000 --density 0.01 --seed 42
    python scripts/generate_problems.py qubo --n 100 --seed 42
"""

import numpy as np
import json
import sys
import argparse
from pathlib import Path


def generate_random_ising(n: int, coupling_std: float = 0.5,
                          field_std: float = 0.1, seed: int = 42) -> dict:
    """
    Generate random Ising spin glass instance.

    Standard construction: J_ij ~ N(0, coupling_std^2), symmetric,
    zero diagonal. h_i ~ N(0, field_std^2).

    Args:
        n: Number of spins
        coupling_std: Standard deviation of coupling distribution
        field_std: Standard deviation of field distribution
        seed: Random seed for reproducibility

    Returns:
        Dictionary with 'J' (coupling matrix), 'h' (fields), and metadata
    """
    rng = np.random.default_rng(seed)

    J = rng.normal(0, coupling_std, (n, n))
    J = (J + J.T) / 2  # Symmetrize
    np.fill_diagonal(J, 0)  # No self-coupling

    h = rng.normal(0, field_std, n)

    # Theoretical bounds
    max_possible_energy = -0.5 * np.sum(np.abs(J)) - np.sum(np.abs(h))

    return {
        "problem_type": "ising",
        "num_spins": n,
        "coupling_std": coupling_std,
        "field_std": field_std,
        "seed": seed,
        "J": J.tolist(),
        "h": h.tolist(),
        "metadata": {
            "num_couplings": int(n * (n - 1) / 2),
            "J_mean": float(np.mean(J)),
            "J_std": float(np.std(J)),
            "h_mean": float(np.mean(h)),
            "h_std": float(np.std(h)),
            "max_possible_energy_bound": float(max_possible_energy)
        }
    }


def generate_random_3sat(num_vars: int, alpha: float = 4.27,
                         seed: int = 42) -> dict:
    """
    Generate random 3-SAT instance at specified clause-to-variable ratio.

    Standard construction: Each clause picks 3 distinct variables uniformly
    at random, each negated independently with probability 0.5.

    The phase transition at alpha = 4.27 is where random 3-SAT transitions
    from almost-always satisfiable to almost-never satisfiable. This is the
    hardest regime for solvers.

    Reference: Mezard, Parisi, Zecchina (2002). "Analytic and Algorithmic
    Solution of Random Satisfiability Problems."

    Args:
        num_vars: Number of Boolean variables
        alpha: Clause-to-variable ratio
        seed: Random seed

    Returns:
        Dictionary with 'clauses', 'num_vars', and metadata
    """
    rng = np.random.default_rng(seed)
    num_clauses = int(num_vars * alpha)

    clauses = []
    for _ in range(num_clauses):
        # Pick 3 distinct variables (1-indexed)
        vars_chosen = rng.choice(num_vars, size=3, replace=False) + 1
        # Random signs
        signs = rng.choice([-1, 1], size=3)
        clause = [int(v * s) for v, s in zip(vars_chosen, signs)]
        clauses.append(clause)

    return {
        "problem_type": "3-sat",
        "num_vars": num_vars,
        "num_clauses": num_clauses,
        "alpha": alpha,
        "seed": seed,
        "clauses": clauses,
        "metadata": {
            "clause_length": 3,
            "phase_transition_alpha": 4.27,
            "regime": "hard" if abs(alpha - 4.27) < 0.1 else
                      ("easy-SAT" if alpha < 4.27 else "easy-UNSAT")
        }
    }


def generate_random_maxcut(n: int, edge_density: float = 0.01,
                           seed: int = 42) -> dict:
    """
    Generate random Max-Cut instance (Erdos-Renyi graph).

    Standard construction: Each edge (i,j) exists independently with
    probability p = edge_density. Unweighted.

    Args:
        n: Number of nodes
        edge_density: Edge probability
        seed: Random seed

    Returns:
        Dictionary with 'adjacency' matrix and metadata
    """
    rng = np.random.default_rng(seed)

    # Generate Erdos-Renyi graph
    adj = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < edge_density:
                adj[i, j] = 1
                adj[j, i] = 1

    num_edges = int(np.sum(adj) // 2)

    return {
        "problem_type": "max-cut",
        "num_nodes": n,
        "num_edges": num_edges,
        "edge_density": edge_density,
        "seed": seed,
        "adjacency": adj.tolist(),
        "metadata": {
            "expected_edges": int(n * (n - 1) / 2 * edge_density),
            "actual_edges": num_edges,
            "avg_degree": float(2 * num_edges / n) if n > 0 else 0,
            "goemans_williamson_bound": 0.878,
            "note": "GW bound: any polynomial-time algorithm achieves at most 0.878 * OPT (assuming P != NP)"
        }
    }


def generate_random_qubo(n: int, density: float = 1.0,
                         seed: int = 42) -> dict:
    """
    Generate random QUBO instance.

    Standard construction: Q_ij ~ N(0, 1) for specified density.

    Args:
        n: Number of binary variables
        density: Fraction of non-zero entries
        seed: Random seed

    Returns:
        Dictionary with 'Q' matrix and metadata
    """
    rng = np.random.default_rng(seed)

    Q = rng.normal(0, 1, (n, n))

    if density < 1.0:
        mask = rng.random((n, n)) < density
        Q *= mask

    # Make upper triangular (standard QUBO form)
    Q = np.triu(Q)

    return {
        "problem_type": "qubo",
        "num_vars": n,
        "density": density,
        "seed": seed,
        "Q": Q.tolist(),
        "metadata": {
            "num_nonzero": int(np.count_nonzero(Q)),
            "Q_mean": float(np.mean(Q)),
            "Q_std": float(np.std(Q)),
            "ising_conversion": "sigma = 2x - 1; J_ij = -Q_ij/4; h_i = -Q_ii/2 - sum_j Q_ij/4"
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate standard benchmark problem instances"
    )
    subparsers = parser.add_subparsers(dest="problem")

    # Ising
    p_ising = subparsers.add_parser("ising", help="Random Ising spin glass")
    p_ising.add_argument("--n", type=int, default=100, help="Number of spins")
    p_ising.add_argument("--coupling-std", type=float, default=0.5)
    p_ising.add_argument("--field-std", type=float, default=0.1)
    p_ising.add_argument("--seed", type=int, default=42)
    p_ising.add_argument("--output", type=str, default=None)

    # SAT
    p_sat = subparsers.add_parser("sat", help="Random 3-SAT")
    p_sat.add_argument("--n", type=int, default=100, help="Number of variables")
    p_sat.add_argument("--alpha", type=float, default=4.27, help="Clause ratio")
    p_sat.add_argument("--seed", type=int, default=42)
    p_sat.add_argument("--output", type=str, default=None)

    # Max-Cut
    p_mc = subparsers.add_parser("maxcut", help="Random Max-Cut")
    p_mc.add_argument("--n", type=int, default=100, help="Number of nodes")
    p_mc.add_argument("--density", type=float, default=0.01, help="Edge density")
    p_mc.add_argument("--seed", type=int, default=42)
    p_mc.add_argument("--output", type=str, default=None)

    # QUBO
    p_qubo = subparsers.add_parser("qubo", help="Random QUBO")
    p_qubo.add_argument("--n", type=int, default=50, help="Number of variables")
    p_qubo.add_argument("--density", type=float, default=1.0)
    p_qubo.add_argument("--seed", type=int, default=42)
    p_qubo.add_argument("--output", type=str, default=None)

    args = parser.parse_args()

    if not args.problem:
        parser.print_help()
        sys.exit(1)

    generators = {
        "ising": lambda: generate_random_ising(args.n, args.coupling_std, args.field_std, args.seed),
        "sat": lambda: generate_random_3sat(args.n, args.alpha, args.seed),
        "maxcut": lambda: generate_random_maxcut(args.n, args.density, args.seed),
        "qubo": lambda: generate_random_qubo(args.n, args.density, args.seed),
    }

    problem = generators[args.problem]()

    # Remove large arrays from console output
    display = {k: v for k, v in problem.items()
               if k not in ("J", "h", "adjacency", "Q", "clauses")}
    print(json.dumps(display, indent=2))

    # Save to file
    output = args.output or f"{args.problem}_n{args.n}_seed{args.seed}.json"
    with open(output, "w") as f:
        json.dump(problem, f)
    print(f"\nSaved to: {output}")


if __name__ == "__main__":
    main()
