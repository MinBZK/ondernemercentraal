from dataclasses import dataclass

from app.core.types import FormNames, TrackTypes


@dataclass
class TrackTypeSettings:
    partner_organization_required: bool
    required_forms: list[FormNames]


track_type_settings: dict[TrackTypes, TrackTypeSettings] = {
    "Ondernemersdienstverlening": TrackTypeSettings(
        partner_organization_required=False,
        required_forms=["Volgrapport", "Eindevaluatie door partner", "Eindevaluatie door adviseur"],
    ),
    "SHVO": TrackTypeSettings(
        partner_organization_required=True,
        required_forms=[],
    ),
}
