import json
import os
import random
import string
import sys
from dataclasses import dataclass

import requests


@dataclass
class Cfg:
    base_url: str = os.environ.get("AETHERIA_BASE_URL", "http://localhost:5001")


def _rand_suffix(n: int = 6) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def main() -> int:
    cfg = Cfg()

    username = f"smoke_{_rand_suffix()}"
    password = "smoke_pass"

    print(f"Base URL: {cfg.base_url}")

    def post(path: str, payload: dict, token: str | None = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = requests.post(f"{cfg.base_url}{path}", headers=headers, json=payload, timeout=30)
        try:
            data = r.json()
        except Exception:
            data = {"_raw": r.text}
        if not r.ok:
            raise RuntimeError(f"POST {path} -> {r.status_code}: {data}")
        return data

    def get(path: str, token: str | None = None) -> dict:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = requests.get(f"{cfg.base_url}{path}", headers=headers, timeout=30)
        try:
            data = r.json()
        except Exception:
            data = {"_raw": r.text}
        if not r.ok:
            raise RuntimeError(f"GET {path} -> {r.status_code}: {data}")
        return data

    # 1) health/version
    health = get("/health")
    version = get("/version")
    print("/health:", health)
    print("/version current:", version.get("current_version"))

    # 2) register/login
    reg = post(
        "/api/auth/register",
        {
            "username": username,
            "password": password,
            "display_name": "Smoke",
            "consents": {"terms_accepted": True, "data_usage_accepted": True},
        },
    )
    print("/api/auth/register:", {k: reg.get(k) for k in ("status", "user_id", "token") if k in reg})

    login = post("/api/auth/login", {"username": username, "password": password})
    token = login.get("token")
    if not token:
        raise RuntimeError(f"Login did not return token: {login}")
    print("/api/auth/login: ok")

    # 3) sessions
    sessions = get("/api/chat/sessions", token=token)
    print("/api/chat/sessions: count=", len((sessions.get("sessions") or [])))

    # 4) consult (non-stream)
    consult = post(
        "/api/chat/consult",
        {"message": "我想問事業方向，請用 2-3 句先問我關鍵問題"},
        token=token,
    )
    print("/api/chat/consult: status=", consult.get("status"), "session_id=", consult.get("session_id"))

    # Print a short preview
    reply = consult.get("reply") or ""
    print("reply preview:")
    print(reply[:200].replace("\n", " "))

    print("\n✓ HTTP smoke test passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print("\n✗ HTTP smoke test failed")
        print(str(exc))
        raise
