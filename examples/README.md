# Examples

Usage examples for the verification tools.

## Generate and Validate

```bash
# Generate a random 3-SAT instance at phase transition
python scripts/generate_problems.py sat --n 100 --alpha 4.27 --seed 42

# Generate a random Ising spin glass
python scripts/generate_problems.py ising --n 100 --seed 42

# Generate a random Max-Cut graph
python scripts/generate_problems.py maxcut --n 100 --density 0.05 --seed 42
```

## Verify Claims

```bash
# List all verifiable claims
python scripts/verify_claims.py --list

# Verify all claims (requires running API)
python scripts/verify_claims.py --api-url http://localhost:5000 --all
```

## Validate Solutions

```bash
# Validate an Ising solution
python scripts/validate_solution.py ising --problem ising_n100.json --solution my_solution.json

# Validate a SAT solution
python scripts/validate_solution.py sat --problem sat_n100.json --solution my_assignment.json
```
