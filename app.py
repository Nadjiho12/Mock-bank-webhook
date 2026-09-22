"""
Mock bank webhook backend for the Real-Time Fraud Intervention agent (N-Sec).

Simulates two endpoints an ElevenLabs Agent Workflow calls as server tools:
  POST /verify  -> in-app biometric challenge result (pass/fail only, no secrets)
  POST /freeze  -> reversible temporary card freeze

Nothing here touches real banking systems. Every response is deterministic
or randomised for demo purposes only, per the challenge's "not deployed in
real production or live settings" rule.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import random
import time

app = FastAPI(title="N-Sec Fraud Agent Mock Webhook")

# in-memory log so the /audit endpoint has something to show in the recording
audit_log = []


class VerifyRequest(BaseModel):
    account_id: str
    alert_id: str


class VerifyResponse(BaseModel):
    result: str  # "pass" | "fail" | "timeout"


class FreezeRequest(BaseModel):
    account_id: str
    alert_id: str


class FreezeResponse(BaseModel):
    status: str  # "ok" | "error"
    reversible: bool


@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    """
    Simulates the bank's in-app biometric challenge.
    The agent never sees a PIN, OTP, or personal data here -- only pass/fail.
    ~10% chance of a simulated timeout, to demonstrate the fail-closed path:
    webhook timeout -> verification/freeze steps fail closed -> human handover.
    """
    roll = random.random()
    if roll < 0.10:
        result = "timeout"
    elif roll < 0.85:
        result = "pass"
    else:
        result = "fail"

    audit_log.append({
        "event": "verify",
        "account_id": req.account_id,
        "alert_id": req.alert_id,
        "result": result,
        "ts": time.time(),
    })
    return VerifyResponse(result=result)


@app.post("/freeze", response_model=FreezeResponse)
def freeze(req: FreezeRequest):
    """
    Simulates a temporary, reversible card freeze.
    This is the ONLY action the agent's tool set can trigger --
    reissue, unfreeze and dispute have no bound tool and route to a human.
    """
    audit_log.append({
        "event": "freeze",
        "account_id": req.account_id,
        "alert_id": req.alert_id,
        "ts": time.time(),
    })
    return FreezeResponse(status="ok", reversible=True)


@app.get("/audit")
def get_audit():
    """Returns the in-memory call log -- stands in for the post-call audit webhook."""
    return {"events": audit_log}


@app.get("/")
def root():
    return {
        "service": "N-Sec fraud agent mock webhook",
        "endpoints": ["/verify", "/freeze", "/audit"],
        "note": "Demo only. No real banking data. Built for the Ignyte x ElevenLabs Future of Voice AI Challenge.",
    }
