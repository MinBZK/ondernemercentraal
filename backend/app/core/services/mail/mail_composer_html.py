from typing import TypedDict

from app.core import settings


class MailRecipient(TypedDict):
    address: str
    name: str


def __get_salutation(recipient: MailRecipient):
    return f"<p>Beste {recipient['name']},</p>"


def _get_closing():
    return f"Met vriendelijke groet,<br />Ondernemer Centraal ({settings.TENANT_NAME})"


def get_mail_html_body(
    content: list[str],
    recipient: MailRecipient,
    metadata: dict[str, str],
    closing=str,
):
    closing = _get_closing()
    salutation = __get_salutation(recipient)
    metadata_html = "".join([f"<p>{k}: {v}</p>" for k, v in metadata.items()])
    html_body = metadata_html + salutation + "".join(["<p>" + p + "</p>" for p in content]) + closing
    return html_body
