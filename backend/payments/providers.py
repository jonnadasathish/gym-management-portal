"""Payment provider abstraction (DEC-018 / AGENTS.md §21.3):

    PaymentService
          |
    PaymentProvider (interface, this module)
          |
    RazorpayProvider (concrete, this module)
    <FutureProvider> (added later without redesigning the domain model)

IMPORTANT — test coverage caveat (recorded honestly, not overstated):
`RazorpayProvider.create_order()` calls Razorpay's real HTTPS API and
CANNOT be exercised by automated tests in this environment (no network
egress to api.razorpay.com, no sandbox credentials configured). It is
implemented against Razorpay's publicly documented Orders API contract but
is **NOT EXECUTED / NOT VERIFIED against the real gateway** — this must be
manually verified against a real Razorpay test-mode account before
relying on it. `verify_webhook_signature()`, by contrast, is a pure
local HMAC computation per Razorpay's documented webhook-verification
algorithm and IS fully unit-tested without any network dependency.
All `payments.services` business-logic tests use `FakePaymentProvider`
(this module) as a test double, so the state-machine/idempotency/refund
logic is verified independent of any real gateway call.
"""

import abc
import hashlib
import hmac


class PaymentProvider(abc.ABC):
    """Every concrete gateway integration implements this. Nothing in
    `payments.services` may import a concrete provider directly — only
    this interface, so a future provider can be swapped in without
    touching the domain model (AGENTS.md §21.3)."""

    @abc.abstractmethod
    def create_order(self, *, amount, currency, receipt, notes=None):
        """Returns a dict with at least `gateway_order_id`."""

    @abc.abstractmethod
    def verify_webhook_signature(self, *, payload_body: bytes, signature: str, secret: str) -> bool:
        """Returns True iff `signature` is a valid signature of
        `payload_body` under `secret`."""

    @abc.abstractmethod
    def process_refund(self, *, gateway_payment_id, amount):
        """Returns a dict with at least `gateway_refund_id`."""


class RazorpayProvider(PaymentProvider):
    """Concrete Razorpay implementation (DEC-005 — Razorpay is the V1
    gateway). See module docstring for the test-coverage caveat on
    `create_order`/`process_refund`.
    """

    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret

    def create_order(self, *, amount, currency, receipt, notes=None):  # pragma: no cover - needs real network/creds
        import razorpay

        client = razorpay.Client(auth=(self.key_id, self.key_secret))
        order = client.order.create(
            {
                "amount": int(amount * 100),  # Razorpay amounts are in paise
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {},
            }
        )
        return {"gateway_order_id": order["id"], "raw": order}

    def verify_webhook_signature(self, *, payload_body: bytes, signature: str, secret: str) -> bool:
        """HMAC-SHA256 of the raw request body using the webhook secret,
        compared to the `X-Razorpay-Signature` header — Razorpay's
        documented webhook verification algorithm. Implemented directly
        (not via the SDK) so it is verifiable with pure unit tests and no
        network dependency."""

        expected = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def process_refund(self, *, gateway_payment_id, amount):  # pragma: no cover - needs real network/creds
        import razorpay

        client = razorpay.Client(auth=(self.key_id, self.key_secret))
        refund = client.payment.refund(gateway_payment_id, {"amount": int(amount * 100)})
        return {"gateway_refund_id": refund["id"], "raw": refund}


class FakePaymentProvider(PaymentProvider):
    """Test double used by `payments.tests.test_services` — lets the
    domain/service logic (state machine, idempotency, refund bookkeeping)
    be fully tested without any real gateway."""

    def __init__(self):
        self.created_orders = []
        self.refunds = []
        self.webhook_secret = "test-secret"

    def create_order(self, *, amount, currency, receipt, notes=None):
        order_id = f"order_fake_{len(self.created_orders) + 1}"
        self.created_orders.append({"amount": amount, "currency": currency, "receipt": receipt})
        return {"gateway_order_id": order_id, "raw": {}}

    def verify_webhook_signature(self, *, payload_body: bytes, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def process_refund(self, *, gateway_payment_id, amount):
        refund_id = f"rfnd_fake_{len(self.refunds) + 1}"
        self.refunds.append({"gateway_payment_id": gateway_payment_id, "amount": amount})
        return {"gateway_refund_id": refund_id, "raw": {}}
