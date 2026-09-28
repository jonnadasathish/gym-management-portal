"""Notification provider abstraction (AGENTS.md §29.1 / OQ-001/002).

No WhatsApp, SMS, or email vendor is integrated. The only concrete
implementation is `ConsoleNotificationProvider`, which writes to the
application log and never performs HTTP.
"""

import logging
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    @abstractmethod
    def send(self, *, to, body, metadata) -> str:
        """Deliver `body` to `to`. Returns a provider message id."""


class ConsoleNotificationProvider(NotificationProvider):
    """Local in-app / log-only delivery. Never calls external HTTP."""

    def send(self, *, to, body, metadata) -> str:
        message_id = f"console-{uuid.uuid4()}"
        logger.info(
            "console notification message_id=%s to=%s body=%s metadata=%s",
            message_id,
            to,
            body,
            metadata,
        )
        return message_id
