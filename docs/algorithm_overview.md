# Algorithm Overview: Simulated Bifurcation Machine

## The Physics

The Daugherty Engine implements the **Simulated Bifurcation Machine (SBM)** -- a classical algorithm inspired by the physics of coupled oscillators undergoing a supercritical pitchfork bifurcation.

The core idea: initialize a network of oscillators near a symmetric equilibrium, then gradually ramp a control parameter past the bifurcation point. The oscillators spontaneously break symmetry and settle into +/-1 states that encode the solution to the optimization problem.

**No quantum hardware required.** The dynamics are entirely classical Hamiltonian mechanics, parallelized on GPUs.

---

## Hamiltonian

The system evolves under:

```
H(x, y) = -1/2 * sum_i y_i^2 + 1/2 * (1 - p(t)) * sum_i x_i^2 - c0/2 * sum_{ij} J_ij x_i x_j
```

Where:
- **x_i**: Position (continuous spin variable)
- **y_i**: Momentum (conjugate variable)
- **p(t)**: Control parameter (pump), ramped from 0 past 1
- **J_ij**: Coupling matrix encoding the optimization problem
- **c0**: Coupling strength

The key force on each oscillator combines:
1. **Bifurcation potential**: `a*x - b*x^3` (creates two stable wells at ±1)
2. **Ising coupling**: `J @ x` (oscillators influence each other)
3. **Local fields**: `h` (bias terms)
4. **Damping**: `-gamma * p` (dissipation for convergence)

---

## Bifurcation Dynamics

Before bifurcation (p < 1):
- All oscillators sit near x = 0 (symmetric equilibrium)
- The potential has a single minimum

After bifurcation (p > 1):
- The single minimum splits into two wells at x ≈ ±1
- Each oscillator "chooses" a well based on the coupling forces
- The network settles into a configuration that minimizes the Ising energy

This is analogous to a ferromagnetic phase transition: above the critical temperature, spins are disordered; below it, they spontaneously align.

---

## Integration

The equations of motion are integrated using **symplectic methods**:

```
p_{n+1} = p_n + F(x_n) * dt      (momentum update)
x_{n+1} = x_n + p_{n+1} * dt      (position update)
```

Symplectic integrators preserve the Hamiltonian structure, preventing artificial energy drift that would corrupt the optimization.

---

## Ising Problem

The target is to minimize:

```
E = -sum_{ij} J_ij * sigma_i * sigma_j - sum_i h_i * sigma_i
```

Where sigma_i ∈ {-1, +1} are discrete spins. The SBM evolves continuous variables x_i and discretizes them at the end: sigma_i = sign(x_i).

The **best discrete energy** encountered during the entire trajectory is retained as the solution.

---

## Algorithm Variants

The SBM literature describes several variants:

| Variant | Coupling Rule | Speed | Accuracy |
|---------|--------------|-------|----------|
| **Ballistic SBM** (bSBM) | Uses continuous x for coupling | Moderate | Higher |
| **Discrete SBM** (dSBM) | Uses sign(x) for coupling | Faster | Slightly lower |
| **Adiabatic SBM** (aSBM) | Slow pump ramp | Slowest | Highest |

The Daugherty Engine uses a proprietary variant with additional stabilization techniques.

---

## Problem Reductions

Any problem reducible to Ising form can be solved:

### QUBO → Ising
```
Given QUBO: minimize x^T Q x, where x ∈ {0,1}^n
Substitute: sigma = 2x - 1 (maps {0,1} to {-1,+1})
Result: J_ij = -Q_ij/4, h_i = -Q_ii/2 - sum_j Q_ij/4
```

### 3-SAT → Ising
Each clause `(l1 OR l2 OR l3)` contributes penalty terms to J and h such that unsatisfied clauses increase the Ising energy. Minimizing energy maximizes clause satisfaction.

### Max-Cut → Ising
For an unweighted graph with adjacency matrix A:
```
J = -A (antiferromagnetic coupling)
h = 0 (no bias)
```
Minimizing the Ising energy maximizes the number of edges between the two partition sets.

---

## References

1. Goto, H. et al. (2019). "Combinatorial optimization by simulating adiabatic bifurcations in nonlinear Hamiltonian systems." *Science Advances*, 5(4).

2. Goto, H. et al. (2021). "High-performance combinatorial optimization based on classical mechanics." *Science Advances*, 7(6).

3. Tatsumura, K. et al. (2021). "Scaling out Ising machines using a multi-chip architecture for simulated bifurcation." *Nature Electronics*, 4.

4. Lucas, A. (2014). "Ising formulations of many NP problems." *Frontiers in Physics*, 2, 5.

---

## What's Proprietary

The Daugherty Engine's competitive advantage is NOT the SBM algorithm itself (which is published). It's the **production engineering**:

- Optimized parameter tuning for specific problem classes
- Adaptive stabilization with momentum-aware thresholds
- Problem-specific configuration presets
- GPU memory management and numerical stability techniques

These details are trade secrets and are not included in this public repository.
