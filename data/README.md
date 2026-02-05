# Data Dictionary

This directory contains the publicly available benchmark data and metadata from the Daugherty Engine.

**No trade secrets are contained in any data file.** All data represents publicly verifiable claims, standard problem definitions, and published comparison metrics.

---

## Files

### `benchmark_claims.json`

Complete set of publicly stated performance claims with verification methodology.

| Key | Description |
|-----|-------------|
| `engine` | Engine identification (name, version, algorithm, author) |
| `claims` | Array of 5 performance claims with parameters, results, and verification instructions |
| `comparison` | D-Wave Advantage vs Daugherty Engine comparison data |
| `hardware` | GPU hardware specifications used for benchmarks |
| `blockchain_verification` | BSV blockchain anchoring methodology |

Each claim includes:
- **id**: Unique identifier (e.g., `SAT-001`)
- **problem_type**: Problem class
- **parameters**: Problem generation parameters (publicly reproducible)
- **claimed_result**: What is claimed (metric, value, display string)
- **verification**: How to independently verify this claim
- **status**: Current verification status

### `problem_types.json`

Comprehensive reference for all supported problem types and their Ising reductions.

| Problem | Reduction | Complexity |
|---------|-----------|------------|
| Ising Model | Native | NP-hard |
| QUBO | Direct mapping | NP-hard |
| 3-SAT | Clause-to-coupling | NP-complete |
| Max-Cut | Adjacency-to-Ising | NP-hard |
| TSP | Via QUBO | NP-hard |
| Graph Coloring | Via QUBO | NP-complete |

Includes the standard QUBO-to-Ising conversion formula and references to Lucas (2014).

---

## Usage

```python
import json

# Load benchmark claims
with open('data/benchmark_claims.json') as f:
    claims = json.load(f)

# List all claims
for claim in claims['claims']:
    print(f"{claim['id']}: {claim['claimed_result']['display']}")

# Load problem type reference
with open('data/problem_types.json') as f:
    types = json.load(f)
```

---

## License

All data in this directory is released under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
