# Verification & Certification System

The Daugherty Engine includes a multi-layer verification system for deployment integrity and performance certification.

---

## Overview

```
FINGERPRINTING           CERTIFICATION            BLOCKCHAIN
(file integrity)         (validation receipts)     (immutable proof)
      |                        |                        |
  SHA-256 hashes     -->  JSON/ASCII receipt  -->  BSV transaction
  semantic hashing        pass/fail summary         timestamped
  layered manifest        content hash              publicly verifiable
```

---

## 1. Fingerprint System

### Purpose
Detect unauthorized modifications to engine source files before deployment.

### How It Works

1. **Compute**: Hash all source files and generate a manifest
2. **Save**: Store manifest as trusted baseline
3. **Verify**: Compare current files against saved manifest
4. **Report**: Flag any modifications

### Semantic Hashing

For Python files, the system uses **AST-based semantic hashing** rather than raw byte hashing:

- Parses the source into an Abstract Syntax Tree
- Normalizes the AST representation
- Hashes the normalized form

This means benign changes (reformatting, comment updates, whitespace) don't trigger false alarms, while any change to actual code logic is detected.

### Layered Manifest

Files are organized into layers:
- **Source layer**: Core algorithm files (`.py`)
- **Config layer**: Configuration and settings
- **Critical files**: Subset of files that MUST match exactly

Each layer gets its own hash. The **master fingerprint** is computed from all layer hashes combined.

### Usage

Fingerprinting is performed internally as part of the Daugherty Engine deployment pipeline. The master fingerprint is included in every certification receipt and blockchain anchor, allowing third parties to verify that published results correspond to a specific engine build.

---

## 2. Certification Receipts

### Purpose
Generate tamper-proof validation certificates that summarize engine testing results.

### What's In a Receipt

Receipts contain ONLY public information:

| Field | Description |
|-------|-------------|
| Engine name & version | "DAUGHERTY ENGINE v3.0.0" |
| Validation results | PASS/FAIL for each solver (Ising, SAT, Max-Cut, QUBO) |
| Master fingerprint | Cryptographic hash of source code |
| Content hash | SHA-256 of the receipt itself |
| Timestamp | UTC ISO 8601 |

### What's NOT In a Receipt

- Parameter values
- Energy results
- Timing data
- Algorithm internals
- Source code

### Receipt Formats

**JSON** (machine-readable):
```json
{
  "receipt_type": "DAUGHERTY_ENGINE_CERTIFICATION",
  "engine": {"name": "DAUGHERTY ENGINE", "version": "3.0.0"},
  "validation": {"all_passed": true},
  "integrity": {"master_fingerprint": "a1b2c3d4..."},
  "content_hash": "e5f67890..."
}
```

**ASCII** (human-readable): Formatted certificate with borders, suitable for printing or display.

---

## 3. Blockchain Anchoring

### Purpose
Provide immutable, timestamped, publicly verifiable proof of certification.

### How It Works

1. Generate certification receipt (JSON)
2. Compute content hash of receipt
3. Publish hash + metadata to BSV blockchain via B:// protocol
4. Record transaction ID in receipt

### What Goes On-Chain

```json
{
  "type": "DAUGHERTY_ENGINE_CERTIFICATION",
  "engine_version": "3.0.0",
  "fingerprint": "a1b2c3d4...",
  "content_hash": "e5f67890...",
  "validation_passed": true
}
```

### Verification

Anyone can verify:
1. Retrieve blockchain transaction via TXID
2. Compare on-chain content hash with locally computed receipt hash
3. If hashes match → receipt is authentic and unmodified

### Properties

| Property | Guaranteed By |
|----------|--------------|
| **Immutability** | Blockchain consensus |
| **Timestamp** | Block inclusion time |
| **Public verifiability** | Anyone can read BSV transactions |
| **No trade secrets** | Only hashes and pass/fail go on-chain |

### Network

- **Blockchain**: BSV (Bitcoin SV)
- **Protocol**: B:// (on-chain data publication)
- **Explorer**: [whatsonchain.com](https://whatsonchain.com)

---

## Full Certification Workflow

The end-to-end workflow runs internally within the Daugherty Engine:

1. **Fingerprint** -- Compute master hash of engine source
2. **Validate** -- Run solver test suite across all problem types
3. **Certify** -- Generate JSON receipt with pass/fail summary
4. **Anchor** -- Publish receipt hash to BSV blockchain
5. **Verify** -- Anyone can compare on-chain hash against a locally held receipt

The public artifacts (certification receipts and blockchain transaction IDs) are referenced in [benchmark_claims.json](../data/benchmark_claims.json).
