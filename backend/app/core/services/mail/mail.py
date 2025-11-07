import smtplib
import uuid
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate

from app.core.settings import settings
from app.util.logger import logger


@dataclass
class MailService:
    """
    Service for sending email with a validated and configured email domain.
    Use send_simple_mail method for sending an email message.
    This service uses environment variables for initialization, these environment variables
    are injected from a configmap and secret.
    Enable DOMAIN and CUSTOMER variables in a configmap and mount this in the deployment.
    E.g. DOMAIN=aanleverportalen.nl and CUSTOMER=ictu-devops
    Enable variables hostname_mailserver and password from the default mail secret.
    """

    domain: str
    client_name: str
    server: str
    password: str
    email_id_prefix: str

    @property
    def __username(self):
        return self.client_name + "@" + self.domain

    def send_simple_mail(
        self,
        sender_address: str,
        recipient_address: str,
        subject: str,
        txt_body: str | None = None,
        html_body: str | None = None,
    ):
        """
        Send an email in txt and/or html.
        :param sender_adress: email address of the sending application e.g., noreply@aanleverportalen.nl
        :param recipient_adress: email address of the recipient e.g., john.doe@example.com
        :param mail_subject: subject of the mail message
        :param txt_body: the text message
        :param html_body: the message in HTML format
        """

        assert html_body is None or txt_body is None, "Either txt_body or html_body must be provided, but not both."

        message_id = f"{self.email_id_prefix}_" + uuid.uuid4().hex[:16]
        msg = EmailMessage()
        if html_body:
            msg.add_alternative(html_body, subtype="html")
        elif txt_body:
            msg.set_content(txt_body)
        else:
            raise ValueError("Either txt_body or html_body must be provided.")

        msg["Subject"] = subject
        msg["From"] = sender_address
        msg["To"] = recipient_address
        msg["Date"] = formatdate(localtime=True)
        msg.add_header("Message-ID", message_id)

        self.send_mail(
            sender_address,
            recipient_address,
            msg,
        )

    def send_mail(self, sender_adress: str, recipient_adress: str, msg: EmailMessage):
        if not settings.EMAIL_ENABLED == "1":
            logger.warning("Email service is disabled, email not sent")
            logger.info(f"Sender address: {sender_adress}")
            logger.info(f"Recipient address: {recipient_adress}")
            logger.info(f"Message: {msg}")
            return
        else:
            try:
                server = smtplib.SMTP(self.server, 25)
                server.set_debuglevel(1 if settings.LOG_LEVEL == "DEBUG" else 0)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.__username, self.password)
                server.send_message(msg, sender_adress, recipient_adress)
                server.quit()
                logger.info(
                    f"Email sent successfully from '{sender_adress}' to '{recipient_adress}' with subject '{msg['Subject']}'"  # noqa
                )
            except smtplib.SMTPException as e:
                logger.error(f"Failed to send email: {e}")
                # raise MailNotSent("Failed to send email")


mail_service = MailService(
    domain=settings.EMAIL_DOMAIN,
    client_name=settings.EMAIL_CLIENT_NAME,
    server=settings.EMAIL_RELAY_HOSTNAME,
    password=settings.EMAIL_RELAY_PASSWORD,
    email_id_prefix=settings.EMAIL_ID_PREFIX,
)
