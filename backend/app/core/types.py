from enum import StrEnum
from typing import Literal

AppointmentTypeName = Literal["Checkgesprek", "Toekomstgesprek", "SHVO intake"]
AppointmentStatus = Literal["Open", "Voltooid", "Geannuleerd"]
TrackStatus = Literal["Nog niet gestart", "Gestart", "Beëindigd"]
RoleNames = Literal["beheerder", "senioradviseur", "adviseur", "partner", "ondernemer"]
FormNames = Literal[
    "Checkgesprek",
    "Volgrapport",
    "Eindevaluatie door partner",
    "Eindevaluatie door adviseur",
    "Toekomstgesprek",
    "IOAZ-aanvraag",
    "BBZ-aanvraag",
    "BBZ-verlenging-aanvraag",
]
TrackTypes = Literal["Ondernemersdienstverlening", "SHVO"]
TrackPriority = Literal["Crisis", "Regulier"]
FileType = Literal["Plan van aanpak", "Overig"]
TenantNames = Literal["Gemeente Utrecht", "Gemeente Den Haag"]
RequiredProducts = Literal["Toekomstgesprek", "SHVO intake"]
FormLinkType = Literal["appointment", "request", "track"]


class FormStatus(StrEnum):
    SUBMITTED = "Ingediend"
    APPROVED = "Goedgekeurd"
    INITIALIZED = "Gestart"
