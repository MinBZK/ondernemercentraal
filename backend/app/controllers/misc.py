from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.core.models as models


@dataclass
class Client:
    @classmethod
    def base_query(cls):
        return select(models.Client).options(
            joinedload(models.Client.cases)
            .joinedload(models.Case.appointments)
            .joinedload(models.Appointment.appointment_type),
            joinedload(models.Client.cases).joinedload(models.Case.tracks),
            joinedload(models.Client.user),
        )


@dataclass
class Case:
    @classmethod
    def get_base_options(cls):
        return (
            joinedload(models.Case.client).joinedload(models.Client.user).joinedload(models.User.partner_organization),
            joinedload(models.Case.tracks).joinedload(models.Track.partner_organization),
            joinedload(models.Case.appointments),
            joinedload(models.Case.advisor).joinedload(models.User.role),
            joinedload(models.Case.advisor).joinedload(models.User.partner_organization),
        )

    @classmethod
    def base_query(cls):
        options = cls.get_base_options()
        return select(models.Case).options(*options)
