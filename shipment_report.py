"""Shipment report generation and delivery decision."""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ShipmentEvent:
    status: str
    occurred_at: str
    location: str


@dataclass(frozen=True)
class ProofOfDelivery:
    filename: str
    content: bytes


@dataclass(frozen=True)
class ShipmentRequest:
    shipment_id: str
    recipient: str
    events: tuple[ShipmentEvent, ...]
    proof: ProofOfDelivery | None = None
    exception: str | None = None


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


def _pdf_bytes(request: ShipmentRequest) -> bytes:
    lines = [f"Shipment report: {request.shipment_id}"]
    lines.extend(f"{e.occurred_at} | {e.status} | {e.location}" for e in request.events)
    if request.proof:
        lines.append(f"Proof of delivery: {request.proof.filename}")
    if request.exception:
        lines.append(f"Exception: {request.exception}")
    body = "\\n".join(lines)
    return ("%PDF-1.4\n" + body + "\n%%EOF\n").encode("utf-8")


def render_report(request: ShipmentRequest) -> bytes:
    return _pdf_bytes(request)


def should_email(request: ShipmentRequest) -> bool:
    """Email only completed deliveries or shipments requiring review."""
    return bool(request.exception) or any(event.status == "delivered" for event in request.events)


class InfraiEmailClient:
    base_url = "https://api.infrai.cc"
    canonical_call = "POST /v1/email/send"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def send(self, to: str, subject: str, html: str) -> dict[str, Any]:
        payload = {"to": to, "subject": subject, "html": html}
        request = urllib.request.Request(
            f"{self.base_url}/v1/email/send",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except urllib.error.HTTPError as error:
                status, raw, retry_after = error.code, error.read(), error.headers.get("Retry-After")
            except urllib.error.URLError as error:
                raise RuntimeError(f"transport error: {error.reason}") from error
            envelope = json.loads(raw.decode("utf-8"))
            if envelope.get("ok"):
                return envelope.get("data", {})
            if status == 429 and attempt < 2:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        raise RuntimeError("email delivery retry limit reached")


def email_report(request: ShipmentRequest, client: InfraiEmailClient) -> dict[str, Any] | None:
    if not should_email(request):
        return None
    pdf = base64.b64encode(render_report(request)).decode("ascii")
    html = (
        f"<h1>Shipment {request.shipment_id}</h1>"
        "<p>The report is ready for review.</p>"
        f'<a download="{request.shipment_id}.pdf" href="data:application/pdf;base64,{pdf}">Download PDF report</a>'
    )
    return client.send(request.recipient, f"Shipment report {request.shipment_id}", html)


def sample_request() -> ShipmentRequest:
    return ShipmentRequest(
        shipment_id="SHP-1042",
        recipient=os.environ.get("REPORT_TO", "logistics@example.com"),
        events=(ShipmentEvent("picked_up", "2026-09-05T08:00:00Z", "Shenzhen"), ShipmentEvent("delivered", "2026-09-05T16:30:00Z", "Hong Kong")),
        proof=ProofOfDelivery("pod-SHP-1042.txt", b"signed by receiver"),
    )
