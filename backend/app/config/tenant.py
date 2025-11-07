from typing import TypedDict

from app.core.types import TenantNames


class TenantConfig(TypedDict):
    primary_color: str
    allowed_gemeentes: list[str]
    residence_locations: list[str]
    company_locations: list[str]


tenant_config: dict[TenantNames, TenantConfig] = {
    "Gemeente Utrecht": {
        "primary_color": "#900900",  # Green
        "allowed_gemeentes": ["Utrecht", "IJsselstein"],
        "residence_locations": [
            "Utrecht",
            "IJsselstein",
            "Stichtse Vecht",
            "Nieuwegein",
            "Lopik",
            "Houten",
        ],
        "company_locations": [
            "Utrecht",
            "IJsselstein",
            "Stichtse Vecht",
            "Nieuwegein",
            "Lopik",
            "Houten",
        ],
    },
    "Gemeente Den Haag": {
        "primary_color": "#0072C6",  # Blue
        "allowed_gemeentes": ["Den Haag", "Leidschendam-Voorburg"],
        "residence_locations": [
            "Den Haag",
            "Leidschendam-Voorburg",
            "Midden-Delfland",
            "Rijswijk",
            "Pijnacker-Nootdorp",
            "Lopik",
            "Houten",
        ],
        "company_locations": ["Den Haag", "Leidschendam-Voorburg"],
    },
}
