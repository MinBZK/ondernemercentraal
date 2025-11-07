from app.core.models import Case, Request
from app.schemas.request import RequestUpsert


async def upsert_request(request: Request, payload: RequestUpsert, case: Case):
    request.name = payload.name
    request.case = case
