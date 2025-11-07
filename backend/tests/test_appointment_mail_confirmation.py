import app.core.models as models
from tests.fixtures import appointment  # noqa: F401


def test_appointment_mail_confirmation(appointment: models.Appointment):  # noqa: F811
    assert appointment
    content = appointment.get_confirmation_mail_content()
    content_str = "".join(content)
    assert "dinsdag 10 juni" in content_str
