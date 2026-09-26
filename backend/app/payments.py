"""
Payment abstraction layer (blueprint section 23) — the POS calls PaymentService,
which delegates to a provider adapter. Only a mock MoMo adapter is implemented
for now; swap in a real MTN MoMo adapter later without touching the POS code.
"""
import uuid
from app import models


class MockMoMoAdapter:
    """Simulates 'customer approves on their phone' -> instantly confirmed for dev/demo."""

    def charge(self, amount: float) -> dict:
        return {
            "status": models.PaymentStatus.CONFIRMED,
            "provider_reference": f"MOCK-MOMO-{uuid.uuid4().hex[:10].upper()}",
        }


class ManualAdapter:
    """Cash / Bank / Card — recorded manually, always confirmed immediately."""

    def charge(self, amount: float) -> dict:
        return {"status": models.PaymentStatus.CONFIRMED, "provider_reference": None}


def get_adapter(method: str):
    if method == models.PaymentMethod.MOMO.value:
        return MockMoMoAdapter()
    return ManualAdapter()
