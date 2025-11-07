from app.config.permissions import Permissions
from app.core.types import FormNames

schemas: dict[FormNames, str] = {
    "Checkgesprek": "./app/config/form_schemas/check.json",
    "Volgrapport": "./app/config/form_schemas/volgrapport.json",
    "Eindevaluatie door partner": "./app/config/form_schemas/eindevaluatie_partner.json",
    "Eindevaluatie door adviseur": "./app/config/form_schemas/eindevaluatie_adviseur.json",
    "Toekomstgesprek": "./app/config/form_schemas/toekomstgesprek.json",
    "BBZ-aanvraag": "./app/config/form_schemas/BBZ-aanvraag.json",
    "BBZ-verlenging-aanvraag": "./app/config/form_schemas/BBZ-verlenging aanvraag.json",
    "IOAZ-aanvraag": "./app/config/form_schemas/IOAZ-aanvraag.json",
}

form_permission_mapping: dict[FormNames, Permissions] = {
    "Eindevaluatie door partner": "track:form:update-eindevaluatie-partnerorganisatie",
    "Eindevaluatie door adviseur": "track:form:update-eindevaluatie-adviseur",
    "Volgrapport": "track:form:update-volggesprek",
    "Checkgesprek": "appointment:form:update-checkgesprek",
    "Toekomstgesprek": "appointment:form:update-toekomstgesprek",
    "BBZ-aanvraag": "request:update",
    "BBZ-verlenging-aanvraag": "request:update",
    "IOAZ-aanvraag": "request:update",
}
