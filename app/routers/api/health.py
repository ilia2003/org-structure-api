from fastapi import APIRouter, Request

from app.schemas import GetHealthcheckResponse


router = APIRouter()


@router.get("/healthcheck", response_model=GetHealthcheckResponse)
async def healthcheck(request: Request) -> GetHealthcheckResponse:
    return GetHealthcheckResponse(
        msg="OK",
        release=request.app.settings.APP_RELEASE,
    )
