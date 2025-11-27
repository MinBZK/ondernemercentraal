from fastapi import APIRouter

from app.core.models.payload_validation import PayloadValidationWrapper

router = APIRouter(tags=["jsonschema"], prefix="/json-schema-validation")


@router.post("/", response_model=PayloadValidationWrapper)
async def validate_json_schema(jsonschema: dict, payload: dict):
    return PayloadValidationWrapper(jsonschema=jsonschema, payload=payload)
