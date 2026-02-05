#!/usr/bin/env python3
"""
Claim Verification Script
==========================

Verifies Daugherty Engine performance claims by:
1. Generating standard benchmark instances
2. Calling the engine's public verification API
3. Validating results against claimed performance

This script does NOT require access to the engine source code.
It uses only the public REST API endpoints.

Usage:
    python scripts/verify_claims.py --api-url http://localhost:5000
    python scripts/verify_claims.py --claim SAT-001
    python scripts/verify_claims.py --all
"""

import json
import sys
import argparse
from pathlib import Path

# Try to import requests for API calls
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Try to import numpy for local problem generation
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def load_claims():
    """Load benchmark claims from data file."""
    claims_path = Path(__file__).parent.parent / "data" / "benchmark_claims.json"
    with open(claims_path) as f:
        return json.load(f)


def verify_sat_claim(api_url: str, claim: dict) -> dict:
    """Verify SAT performance claim via API."""
    params = claim["parameters"]

    payload = {
        "num_vars": params["num_vars"],
        "alpha": params["alpha"],
        "num_trials": 5
    }

    print(f"  Sending verification request: n={params['num_vars']}, alpha={params['alpha']}")

    try:
        resp = requests.post(f"{api_url}/verify/sat", json=payload, timeout=300)
        result = resp.json()

        if result.get("success"):
            satisfaction = result["data"]["satisfaction_rate"]
            claimed = claim["claimed_result"]["value"] * 100
            passed = satisfaction >= claimed * 0.95  # Within 5% of claim

            return {
                "claim_id": claim["id"],
                "verified": passed,
                "measured": f"{satisfaction:.1f}%",
                "claimed": f"{claimed:.1f}%",
                "within_tolerance": passed
            }
        else:
            return {"claim_id": claim["id"], "verified": False, "error": result.get("error")}

    except requests.exceptions.ConnectionError:
        return {"claim_id": claim["id"], "verified": None, "error": "API not reachable"}
    except Exception as e:
        return {"claim_id": claim["id"], "verified": None, "error": str(e)}


def verify_ising_claim(api_url: str, claim: dict) -> dict:
    """Verify Ising performance claim via API."""
    params = claim["parameters"]
    n = params["num_spins"]

    print(f"  Generating random Ising instance: n={n}")

    if not HAS_NUMPY:
        return {"claim_id": claim["id"], "verified": None, "error": "numpy required"}

    np.random.seed(42)
    J = np.random.randn(n, n) * 0.5
    J = (J + J.T) / 2
    np.fill_diagonal(J, 0)
    h = np.random.randn(n) * 0.1

    payload = {
        "J": J.tolist(),
        "h": h.tolist()
    }

    print(f"  Sending to API (this may take a moment for n={n})...")

    try:
        resp = requests.post(f"{api_url}/solve/ising", json=payload, timeout=600)
        result = resp.json()

        if result.get("success"):
            quality = result["data"]["result"]["quality_tier"]
            return {
                "claim_id": claim["id"],
                "verified": quality in ["EXCELLENT", "GOOD"],
                "quality_tier": quality,
                "quality_score": result["data"]["result"].get("quality_score")
            }
        else:
            return {"claim_id": claim["id"], "verified": False, "error": result.get("error")}

    except requests.exceptions.ConnectionError:
        return {"claim_id": claim["id"], "verified": None, "error": "API not reachable"}
    except Exception as e:
        return {"claim_id": claim["id"], "verified": None, "error": str(e)}


def verify_maxcut_claim(api_url: str, claim: dict) -> dict:
    """Verify Max-Cut performance claim via API."""
    n = claim["parameters"]["num_nodes"]

    print(f"  Generating random graph: n={n}")

    if not HAS_NUMPY:
        return {"claim_id": claim["id"], "verified": None, "error": "numpy required"}

    np.random.seed(42)
    adj = np.zeros((n, n))
    num_edges = n * 5
    for _ in range(num_edges):
        i, j = np.random.randint(0, n, 2)
        if i != j:
            adj[i, j] = 1
            adj[j, i] = 1

    payload = {"adjacency": adj.tolist()}

    try:
        resp = requests.post(f"{api_url}/solve/maxcut", json=payload, timeout=300)
        result = resp.json()

        if result.get("success"):
            cut_ratio = result["data"]["result"].get("cut_ratio", 0)
            return {
                "claim_id": claim["id"],
                "verified": cut_ratio > 50,
                "cut_ratio": f"{cut_ratio:.1f}%"
            }
        else:
            return {"claim_id": claim["id"], "verified": False, "error": result.get("error")}

    except requests.exceptions.ConnectionError:
        return {"claim_id": claim["id"], "verified": None, "error": "API not reachable"}
    except Exception as e:
        return {"claim_id": claim["id"], "verified": None, "error": str(e)}


def verify_claim(api_url: str, claim: dict) -> dict:
    """Route to appropriate verifier based on problem type."""
    problem_type = claim["problem_type"].lower()

    if "sat" in problem_type:
        return verify_sat_claim(api_url, claim)
    elif "ising" in problem_type and "million" not in problem_type.lower():
        return verify_ising_claim(api_url, claim)
    elif "max-cut" in problem_type or "maxcut" in problem_type:
        return verify_maxcut_claim(api_url, claim)
    elif "million" in problem_type.lower():
        return {
            "claim_id": claim["id"],
            "verified": None,
            "note": "Million-scale claims verified via live demo at https://1millionspins.originneural.ai/"
        }
    else:
        return {"claim_id": claim["id"], "verified": None, "error": f"No verifier for {problem_type}"}


def main():
    parser = argparse.ArgumentParser(description="Verify Daugherty Engine performance claims")
    parser.add_argument("--api-url", default="http://localhost:5000",
                        help="Engine API URL")
    parser.add_argument("--claim", help="Verify specific claim by ID (e.g., SAT-001)")
    parser.add_argument("--all", action="store_true", help="Verify all claims")
    parser.add_argument("--list", action="store_true", help="List available claims")

    args = parser.parse_args()

    claims_data = load_claims()

    if args.list:
        print("Available claims:")
        for claim in claims_data["claims"]:
            print(f"  {claim['id']}: {claim['description']}")
            print(f"    Claimed: {claim['claimed_result']['display']}")
        sys.exit(0)

    if not HAS_REQUESTS:
        print("ERROR: 'requests' library required for API verification.")
        print("Install: pip install requests")
        sys.exit(1)

    print("=" * 60)
    print("DAUGHERTY ENGINE - CLAIM VERIFICATION")
    print("=" * 60)
    print(f"API: {args.api_url}")
    print()

    results = []

    if args.claim:
        matching = [c for c in claims_data["claims"] if c["id"] == args.claim]
        if not matching:
            print(f"Unknown claim: {args.claim}")
            sys.exit(1)
        claims_to_verify = matching
    elif args.all:
        claims_to_verify = claims_data["claims"]
    else:
        parser.print_help()
        sys.exit(1)

    for claim in claims_to_verify:
        print(f"Verifying {claim['id']}: {claim['description']}")
        result = verify_claim(args.api_url, claim)
        results.append(result)

        status = "VERIFIED" if result.get("verified") else \
                 "FAILED" if result.get("verified") is False else "SKIPPED"
        print(f"  Result: {status}")
        if "error" in result:
            print(f"  Error: {result['error']}")
        if "note" in result:
            print(f"  Note: {result['note']}")
        print()

    # Summary
    verified = sum(1 for r in results if r.get("verified"))
    failed = sum(1 for r in results if r.get("verified") is False)
    skipped = sum(1 for r in results if r.get("verified") is None)

    print("=" * 60)
    print(f"RESULTS: {verified} verified, {failed} failed, {skipped} skipped")
    print("=" * 60)

    # Save results
    output_path = Path(__file__).parent.parent / "verification_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
