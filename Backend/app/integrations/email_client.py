import logging

logger = logging.getLogger(__name__)


class EmailClient:
    """Client wrapper for sending transactional emails (SMTP / SendGrid)."""

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        # TODO: Implement email sending integration in future phase.
        logger.info("EmailClient: Sending email stub to %s", to_email)
        return True
