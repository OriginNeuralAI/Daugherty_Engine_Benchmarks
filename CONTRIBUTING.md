# Contributing

We welcome independent verification, benchmarking comparisons, and constructive feedback.

---

## How to Contribute

### 1. Verify Our Claims

The most valuable contribution is **independent verification** of our performance claims.

```bash
# List all verifiable claims
python scripts/verify_claims.py --list

# Verify via API (requires engine access)
python scripts/verify_claims.py --api-url http://localhost:5000 --all
```

You can also verify **without API access** by:
1. Generating standard benchmark instances with `scripts/generate_problems.py`
2. Solving them with your own solver
3. Comparing results using `scripts/validate_solution.py`

### 2. Benchmark Comparisons

We encourage comparing the Daugherty Engine against:
- Simulated Annealing (SA)
- Genetic Algorithms (GA)
- D-Wave quantum annealing
- Other SBM implementations
- SDP relaxation (for Max-Cut)

Use the standard problem generators in `scripts/generate_problems.py` to ensure fair comparison on identical instances.

### 3. Report Issues

If you find:
- Errors in our data or documentation
- Claims that don't match your verification results
- Bugs in the public scripts

Please open an issue with:
- Problem type and size
- Your solver configuration
- Your results vs our claims
- Reproduction steps

---

## What We Cannot Accept

Due to trade secret protection:
- We cannot share proprietary parameter values
- We cannot disclose internal algorithm details beyond what's in `docs/algorithm_overview.md`
- Pull requests to the private engine repository are not accepted

---

## Code of Conduct

- Be rigorous and precise in verification claims
- Report both confirming and disconfirming results
- Provide reproduction steps for all findings
- Respect intellectual property boundaries

---

## Attribution

All verified results (confirming or disconfirming) will be acknowledged in this repository.
