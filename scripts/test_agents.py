"""Tests métier des agents Ventes, Support et Marketing via l'API."""

import json
import os
import sys
import time

import httpx

BASE_URL = os.getenv("API_URL", "http://localhost:8000")

TESTS = [
    {
        "name": "Agent Ventes — CA total",
        "thread_id": "test-sales-1",
        "message": "Quel est le chiffre d'affaires total de toutes les ventes ?",
        "expect_agent": "sales_agent",
    },
    {
        "name": "Agent Support — réclamations lenteur",
        "thread_id": "test-support-1",
        "message": "Quelles réclamations clients concernent la lenteur ou les problèmes de performance ?",
        "expect_agent": "support_agent",
    },
    {
        "name": "Agent Marketing — clients inactifs",
        "thread_id": "test-marketing-1",
        "message": "Quels clients sont inactifs ou ont un faible montant total dépensé ?",
        "expect_agent": "marketing_agent",
    },
]


def _safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def run_test(client: httpx.Client, test: dict) -> dict:
    print(f"\n--- {test['name']} ---")
    print(f"Question: {test['message']}")

    start = time.time()
    response = client.post(
        f"{BASE_URL}/chat",
        json={"message": test["message"], "thread_id": test["thread_id"]},
        timeout=300.0,
    )
    elapsed = time.time() - start

    result = {
        "name": test["name"],
        "status_code": response.status_code,
        "elapsed_s": round(elapsed, 1),
        "ok": False,
    }

    if response.status_code != 200:
        result["error"] = response.text
        print(f"ERREUR HTTP {response.status_code}: {response.text[:200]}")
        return result

    data = response.json()
    agent = data.get("agent", "")
    reply = data.get("response", "")

    result["agent"] = agent
    result["response_preview"] = reply[:300]
    result["ok"] = response.status_code == 200 and len(reply) > 20

    print(f"Agent: {agent} (attendu: {test.get('expect_agent', '?')})")
    print(f"Reponse ({elapsed:.1f}s): {_safe(reply[:250])}...")

    # Historique persistant
    hist = client.get(f"{BASE_URL}/history/{test['thread_id']}", timeout=30.0)
    if hist.status_code == 200:
        msg_count = len(hist.json().get("messages", []))
        result["history_count"] = msg_count
        print(f"Historique persisté: {msg_count} message(s)")

    return result


def main():
    print(f"Tests métier — {BASE_URL}")
    health = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    print("Health:", health.json())

    results = []
    with httpx.Client() as client:
        for test in TESTS:
            results.append(run_test(client, test))

    passed = sum(1 for r in results if r["ok"])
    print(f"\n=== Résultat: {passed}/{len(results)} tests OK ===")
    print(json.dumps(results, ensure_ascii=True, indent=2))
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
