# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| v1.0.x (current) | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, **please report it responsibly.**

### How to Report

1. **Email**: Send a detailed report to **security@originneural.ai**
2. **Subject line**: `[SECURITY] Daugherty_Engine_Benchmarks -- <brief description>`
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Resolution timeline**: Depends on severity; critical issues patched within 72 hours

### Scope

This repository contains **benchmark tools and validation scripts**. The primary security concerns are:

| Area | Concern |
|---|---|
| **API interaction** | `verify_claims.py` makes HTTP requests to the engine's public API |
| **Script injection** | Malicious input to problem generators or validators |
| **Data integrity** | Tampered benchmark claims or problem definitions |
| **Supply chain** | Compromised dependencies (numpy, requests, matplotlib) |

### Out of Scope

- The Daugherty Engine itself (proprietary; not in this repository)
- Blockchain anchoring infrastructure
- Third-party solver implementations

### API Security Model

The `verify_claims.py` script interacts with the engine's public verification API:

| Aspect | Policy |
|---|---|
| **Authentication** | Post-quantum cryptography (Dilithium/ML-DSA) for production endpoints |
| **Rate limits** | Per-key limits; see `docs/api_security.md` for details |
| **Data retention** | Inputs are not stored. Outputs are blockchain-anchored if requested. |
| **Transport** | TLS 1.3 minimum |

### Local-Only Scripts

`generate_problems.py` and `validate_solution.py` are fully local:

- No network calls
- No file system access outside the repository
- Deterministic with fixed seeds
- All computation uses standard NumPy operations

### Dependency Policy

- Dependencies are listed in `scripts/requirements.txt` (numpy, requests, matplotlib)
- `requests` is optional -- scripts degrade gracefully without it
- No post-install hooks or build scripts

## Responsible Disclosure

We follow coordinated disclosure. Please do not open public issues for security vulnerabilities. We will credit reporters in the fix commit unless anonymity is requested.
