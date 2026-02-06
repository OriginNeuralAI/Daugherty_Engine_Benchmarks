# Benchmark Methodology

## Problem Generation

All benchmark instances are generated using standard, published algorithms -- no proprietary methods. Seeds are fixed for reproducibility.

| Problem Type | Generator | Key Parameters |
|---|---|---|
| **Random Ising** | Gaussian J_ij couplings + random fields | n, coupling_std, field_std, seed |
| **3-SAT** | Uniform random k-SAT at clause ratio alpha | n, alpha (4.27 = phase transition), seed |
| **Max-Cut** | Erdos-Renyi random graphs | n, edge density, seed |
| **QUBO** | Dense N(0,1) matrices | n, seed |

Generate instances:

```bash
python scripts/generate_problems.py ising --n 1000 --seed 42
python scripts/generate_problems.py sat --n 1000 --alpha 4.27 --seed 42
python scripts/generate_problems.py maxcut --n 1000 --density 0.01 --seed 42
python scripts/generate_problems.py qubo --n 100 --seed 42
```

## Solution Validation

All validators use standard mathematical definitions:

- **Ising**: Energy E = -sum(J_ij * s_i * s_j) - sum(h_i * s_i), compared to random baseline
- **SAT**: Count satisfied clauses, report satisfaction rate
- **Max-Cut**: Compute cut value, compare to Goemans-Williamson 0.878 approximation bound
- **QUBO**: Compute x^T Q x objective value

## Verified Claims

See [`data/benchmark_claims.json`](../data/benchmark_claims.json) for the 5 verified performance claims with full parameters, hardware specifications, and verification methods.

## Hardware

| GPU | VRAM | Cost |
|---|---|---|
| NVIDIA RTX A6000 | 48 GB | $1.57/hr (cloud) |
| NVIDIA RTX 5070 Ti | 17.1 GB GDDR7 | Consumer GPU |
