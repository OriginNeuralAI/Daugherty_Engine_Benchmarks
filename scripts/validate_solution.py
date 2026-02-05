#!/usr/bin/env python3
"""
Solution Validator
===================

Validates solutions to combinatorial optimization problems.
All validation logic uses standard mathematical definitions --
no proprietary algorithms.

This tool can verify:
- Ising solutions: check energy computation
- SAT solutions: check clause satisfaction
- Max-Cut solutions: check cut value
- QUBO solutions: check objective value

Usage:
    python scripts/validate_solution.py ising --problem problem.json --solution solution.json
    python scripts/validate_solution.py sat --problem problem.json --solution solution.json
"""

import numpy as np
import json
import sys
import argparse


def validate_ising(J, h, spins) -> dict:
    """
    Validate an Ising solution.

    Computes: H = -sum_{ij} J_ij * sigma_i * sigma_j - sum_i h_i * sigma_i

    Args:
        J: Coupling matrix (n x n)
        h: Local field vector (n)
        spins: Spin configuration (list of +1/-1)

    Returns:
        Validation result dictionary
    """
    J = np.array(J, dtype=np.float64)
    h = np.array(h, dtype=np.float64)
    sigma = np.array(spins, dtype=np.float64)
    n = len(spins)

    errors = []

    # Check spin values
    for i, s in enumerate(spins):
        if s not in [-1, 1]:
            errors.append(f"Spin {i} has invalid value {s} (must be +1 or -1)")

    if len(spins) != J.shape[0]:
        errors.append(f"Spin count {len(spins)} != problem size {J.shape[0]}")

    if errors:
        return {"valid": False, "errors": errors}

    # Compute energy
    energy = -0.5 * sigma @ J @ sigma - np.dot(h, sigma)

    # Random baseline (average over many random configurations)
    num_samples = 1000
    rng = np.random.default_rng(0)
    random_energies = []
    for _ in range(num_samples):
        rand_spins = rng.choice([-1, 1], size=n).astype(np.float64)
        rand_energy = -0.5 * rand_spins @ J @ rand_spins - np.dot(h, rand_spins)
        random_energies.append(rand_energy)

    mean_random = np.mean(random_energies)
    std_random = np.std(random_energies)
    best_random = np.min(random_energies)

    improvement_over_mean = (mean_random - energy) / abs(mean_random) * 100 if mean_random != 0 else 0
    improvement_over_best = (best_random - energy) / abs(best_random) * 100 if best_random != 0 else 0

    return {
        "valid": True,
        "energy": float(energy),
        "random_baseline": {
            "mean_energy": float(mean_random),
            "std_energy": float(std_random),
            "best_of_1000": float(best_random)
        },
        "improvement_over_random_mean": f"{improvement_over_mean:.1f}%",
        "improvement_over_random_best": f"{improvement_over_best:.1f}%",
        "sigma_below_mean": float((mean_random - energy) / std_random) if std_random > 0 else 0
    }


def validate_sat(clauses, num_vars, assignment) -> dict:
    """
    Validate a SAT solution.

    Checks each clause against the assignment.

    Args:
        clauses: List of clauses in CNF format
        num_vars: Number of variables
        assignment: List of 0/1 values (0=False, 1=True)

    Returns:
        Validation result dictionary
    """
    errors = []

    if len(assignment) != num_vars:
        errors.append(f"Assignment length {len(assignment)} != num_vars {num_vars}")

    for i, a in enumerate(assignment):
        if a not in [0, 1]:
            errors.append(f"Assignment[{i}] has invalid value {a} (must be 0 or 1)")

    if errors:
        return {"valid": False, "errors": errors}

    satisfied = 0
    unsatisfied_clauses = []

    for idx, clause in enumerate(clauses):
        clause_sat = False
        for lit in clause:
            var = abs(lit) - 1
            if lit > 0 and assignment[var] == 1:
                clause_sat = True
                break
            elif lit < 0 and assignment[var] == 0:
                clause_sat = True
                break
        if clause_sat:
            satisfied += 1
        else:
            if len(unsatisfied_clauses) < 10:
                unsatisfied_clauses.append(idx)

    fraction = satisfied / len(clauses) if clauses else 1.0
    alpha = len(clauses) / num_vars if num_vars > 0 else 0

    return {
        "valid": True,
        "clauses_satisfied": satisfied,
        "clauses_total": len(clauses),
        "satisfaction_rate": round(fraction * 100, 2),
        "satisfies_all": satisfied == len(clauses),
        "alpha": round(alpha, 3),
        "phase_transition_regime": "hard" if abs(alpha - 4.27) < 0.1 else
                                   ("easy-SAT" if alpha < 4.27 else "easy-UNSAT"),
        "first_unsatisfied": unsatisfied_clauses[:5] if unsatisfied_clauses else None
    }


def validate_maxcut(adjacency, partition) -> dict:
    """
    Validate a Max-Cut solution.

    Counts edges between the two partition sets.

    Args:
        adjacency: Graph adjacency matrix
        partition: List of +1/-1 values (partition assignment)

    Returns:
        Validation result dictionary
    """
    adj = np.array(adjacency)
    n = adj.shape[0]

    errors = []
    if len(partition) != n:
        errors.append(f"Partition length {len(partition)} != graph size {n}")

    for i, p in enumerate(partition):
        if p not in [-1, 1]:
            errors.append(f"Partition[{i}] has invalid value {p} (must be +1 or -1)")

    if errors:
        return {"valid": False, "errors": errors}

    cut_value = 0
    total_edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] != 0:
                total_edges += 1
                if partition[i] != partition[j]:
                    cut_value += int(adj[i, j])

    cut_ratio = cut_value / total_edges if total_edges > 0 else 0

    set_a = sum(1 for p in partition if p == 1)
    set_b = n - set_a

    return {
        "valid": True,
        "cut_value": cut_value,
        "total_edges": total_edges,
        "cut_ratio": round(cut_ratio * 100, 2),
        "partition_balance": f"{set_a}/{set_b}",
        "goemans_williamson_bound": round(0.878 * total_edges, 1),
        "note": "GW bound is theoretical maximum for poly-time algorithms"
    }


def validate_qubo(Q, solution) -> dict:
    """
    Validate a QUBO solution.

    Computes: objective = x^T Q x

    Args:
        Q: QUBO matrix
        solution: Binary solution vector (list of 0/1)

    Returns:
        Validation result dictionary
    """
    Q = np.array(Q, dtype=np.float64)
    x = np.array(solution, dtype=np.float64)
    n = len(solution)

    errors = []
    if len(solution) != Q.shape[0]:
        errors.append(f"Solution length {len(solution)} != Q size {Q.shape[0]}")

    for i, v in enumerate(solution):
        if v not in [0, 1]:
            errors.append(f"Solution[{i}] has invalid value {v} (must be 0 or 1)")

    if errors:
        return {"valid": False, "errors": errors}

    objective = float(x @ Q @ x)

    # Random baseline
    rng = np.random.default_rng(0)
    random_objectives = []
    for _ in range(1000):
        rand_x = rng.choice([0, 1], size=n).astype(np.float64)
        random_objectives.append(float(rand_x @ Q @ rand_x))

    return {
        "valid": True,
        "objective": objective,
        "num_ones": int(sum(solution)),
        "random_baseline": {
            "mean_objective": float(np.mean(random_objectives)),
            "best_of_1000": float(np.min(random_objectives))
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Validate optimization solutions")
    parser.add_argument("problem_type", choices=["ising", "sat", "maxcut", "qubo"])
    parser.add_argument("--problem", required=True, help="Problem JSON file")
    parser.add_argument("--solution", required=True, help="Solution JSON file")

    args = parser.parse_args()

    with open(args.problem) as f:
        problem = json.load(f)
    with open(args.solution) as f:
        solution = json.load(f)

    if args.problem_type == "ising":
        result = validate_ising(problem["J"], problem["h"], solution["spins"])
    elif args.problem_type == "sat":
        result = validate_sat(problem["clauses"], problem["num_vars"], solution["assignment"])
    elif args.problem_type == "maxcut":
        result = validate_maxcut(problem["adjacency"], solution["partition"])
    elif args.problem_type == "qubo":
        result = validate_qubo(problem["Q"], solution["solution"])

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
