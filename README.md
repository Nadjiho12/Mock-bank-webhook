# N-Sec — Real-Time Fraud Intervention (mock webhook)

Prototype backend for the Ignyte × ElevenLabs Future of Voice AI Challenge,
Track 1 (Banking & Insurance), use case: **Real-Time Fraud Intervention**.

## What this is

An outbound voice agent calls a customer the moment a fraud alert fires,
verifies them through the bank's own approved challenge flow (no PIN or
password), and can apply one pre-approved, reversible protective action —
a temporary card freeze. Anything irreversible goes to a human analyst.

This repo is the mock backend that stands in for the bank's systems while
the agent runs on the ElevenLabs platform:

- `POST /verify` — simulates the bank's in-app biometric challenge.
  Returns **pass / fail / timeout only** — no PIN, OTP, or personal data
  ever crosses this endpoint. The agent never has access to a credential,
  only the result.
- `POST /freeze` — simulates a temporary, **reversible** card freeze. This
  is the only account action the agent's tool set can trigger. Reissue,
  unfreeze and dispute have no bound tool and are handled by a person.
- `GET /audit` — returns the in-memory event log, standing in for a
  post-call audit trail.

## What's real vs. mocked

| Component | Status |
|---|---|
| ElevenLabs Agent Workflow (multi-step call flow) | Real, built on the platform |
| This webhook service | **Mocked** — no real banking system behind it |
| Biometric app | **Mocked** — `/verify` returns a randomised result |
| Core-banking freeze | **Mocked** — `/freeze` always succeeds |
| Human analyst queue | **Not implemented** — shown as a connection point only |

This is a Stage 1 proof-of-build only. Per the challenge rules, nothing
here is deployed against real production or live banking data.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then POST to `http://localhost:8000/verify` with:
```json
{"account_id": "demo-123", "alert_id": "alert-001"}
```

## Deploy (Render, free tier)

1. Push this repo to GitHub.
2. On Render: New → Web Service → connect this repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Copy the resulting public URL into the ElevenLabs agent's webhook tool
   configuration for `/verify` and `/freeze`.

## Context

Built by N-Sec (solo) for the Sep 23 2026 Stage 1 submission to the
Ignyte × ElevenLabs Future of Voice AI Challenge.
