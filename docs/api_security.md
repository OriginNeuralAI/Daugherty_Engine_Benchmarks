# API Security Architecture

The Daugherty Engine REST API implements multiple security layers to enable public verification of performance claims while protecting proprietary algorithm details.

---

## Design Philosophy

**Problem:** Users need to verify performance claims, but raw output (energy values, timing data, iteration counts) could reveal algorithm characteristics.

**Solution:** A security middleware layer that sanitizes all outputs into categories and quality tiers rather than exposing raw numerical data.

---

## Security Layers

### 1. Rate Limiting

| Parameter | Value |
|-----------|-------|
| Requests per window | 100 |
| Window duration | 1 hour |
| Scope | Per client (API key) |

Prevents abuse and ensures fair access across clients.

### 2. Input Validation

Maximum problem sizes enforced at the API boundary:

| Problem Type | Maximum Size |
|-------------|-------------|
| Ising | 5,000 spins |
| SAT | 2,000 variables |
| SAT clauses | 10,000 |
| Max-Cut | 5,000 nodes |
| QUBO | 5,000 variables |

All inputs are validated for:
- Correct data types and structure
- Reasonable value ranges
- Matrix symmetry (where required)
- Valid literal references (SAT)

### 3. Output Sanitization

**Energy values** are never returned directly. Instead:

| Raw Output | Sanitized Output |
|-----------|-----------------|
| Energy = -1234.56 | Quality Score: 87.3 |
| | Quality Tier: EXCELLENT |

Quality tiers:
- **EXCELLENT** (90-100): Outstanding optimization
- **GOOD** (70-89): Strong result
- **FAIR** (50-69): Acceptable
- **POOR** (0-49): Below expectations

**Timing data** is obfuscated:
- ±10% random noise added to all timing values
- Only coarse categories returned (FAST, NORMAL, MODERATE, EXTENDED, LONG)
- Prevents timing-based side-channel analysis

**Solutions** are hashed:
- SHA-256 hash of solution (first 16 characters)
- Enables verification without full solution disclosure
- Users can hash their own solutions for comparison

### 4. PQC Authentication

Authenticated endpoints use **Post-Quantum Cryptographic** authentication:

| Feature | Detail |
|---------|--------|
| Hash Algorithm | SHA3-256 |
| Key Registration | BSV blockchain-anchored |
| Replay Protection | One-time fragments per request |
| Rate Limiting | 1,024 requests per key, tier-based |

---

## Public vs Authenticated Endpoints

### Public (No Auth Required)

These endpoints exist specifically for claim verification:

```
GET  /claims              # List all verifiable performance claims
POST /verify/sat          # Verify SAT performance claim
POST /verify/ising        # Verify Ising performance claim
POST /verify/maxcut       # Verify Max-Cut performance claim
GET  /health              # API health check
GET  /limits              # Problem size limits
```

### Authenticated (PQC Key Required)

```
POST /solve/ising         # Solve Ising problem
POST /solve/sat           # Solve SAT problem
POST /solve/maxcut        # Solve Max-Cut problem
POST /solve/qubo          # Solve QUBO problem
```

---

## Response Format

All responses follow a standardized structure:

```json
{
  "success": true,
  "data": {
    "result": {
      "quality_score": 87.3,
      "quality_tier": "EXCELLENT",
      "solution_hash": "a1b2c3d4e5f67890",
      "timing": {
        "category": "FAST",
        "display": "< 1 second"
      }
    }
  },
  "timestamp": "2026-01-24T12:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "message": "Problem size 6000 exceeds maximum 5000",
    "code": 400
  },
  "timestamp": "2026-01-24T12:00:00Z"
}
```

---

## What's NOT Exposed

The following are never included in API responses:
- Raw energy values
- Precise timing data
- Iteration counts
- Internal solver state
- Configuration parameters
- Convergence patterns
- Algorithm variant selection
