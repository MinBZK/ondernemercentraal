from dataclasses import dataclass

from fastapi import BackgroundTasks

from app.core.models import Case, Client, PartnerOrganization, User
from app.core.services.mail import get_mail_html_body, mail_service
from app.core.services.mail.mail_composer_html import MailRecipient
from app.util.logger import logger


@dataclass
class EmailNotifier:
    background_task: BackgroundTasks

    def __notify(self, recipient: MailRecipient, content: list[str], subject: str):
        self.background_task.add_task(
            mail_service.send_simple_mail,
            sender_address="noreply@i8s.nl",
            recipient_address=recipient["address"],
            subject=subject,
            html_body=get_mail_html_body(content, recipient=recipient, metadata={}),
        )

    def notify_partner_organization(self, partner_organization: PartnerOrganization, content: list[str], subject: str):
        if not partner_organization.email:
            logger.warning(
                f"Notification with subject '{subject}' not sent to user '{partner_organization.name}' because email is not set."  # noqa
            )
            return
        self.__notify(
            {
                "name": partner_organization.name,
                "address": partner_organization.email,
            },
            content,
            subject,
        )

    def notify_user(
        self,
        user: User,
        content: list[str],
        subject: str,
        case: Case | None = None,
        case_link_label: str | None = "Bekijk hier het relevante dossier",
    ):
        if not user.email:
            logger.warning(
                f"Notification with subject '{subject}' not sent to user '{user.name}' because email is not set."
            )
            return

        if case is not None:
            content.append(
                f"<a href='{case.url}'>{case_link_label}</a>",
            )

        self.__notify(
            {
                "name": user.name,
                "address": user.email,
            },
            content,
            subject,
        )

    def notify_client(self, client: Client, content: list[str], subject: str, email_must_be_confirmed: bool = True):
        if email_must_be_confirmed and not client.email_confirmed:
            logger.warning(
                f"Notification with subject '{subject}' not sent to client '{client.written_name}' because email is not confirmed."  # noqa
            )
            return
        self.__notify(
            recipient={
                "name": client.written_name,
                "address": client.email,
            },
            content=content,
            subject=subject,
        )
