import mongoengine
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from src.exceptions import APIException, OAuth2Exception
from src.models.error import APIError, OAuth2Error
from src.routers.account_manager import router as account_manager_router
from src.routers.api import router as api_router

app: FastAPI = FastAPI(title="Socialify API", version="0.2.0")

app.include_router(account_manager_router)
app.include_router(api_router)

templates: Jinja2Templates = Jinja2Templates(directory="templates")
mongoengine.connect("socialify-me")


@app.exception_handler(404)
def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(405)
def method_not_allowed_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=405,
        content=APIError(
            code="method_not_allowed", message="Method Not Allowed"
        ).dict(),
    )


@app.exception_handler(500)
def internal_server_error_exception_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=APIError(
            code="internal_server_error", message=f"Internal Server Error: {str(exc)}"
        ).dict(),
    )


@app.exception_handler(RequestValidationError)
def request_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=APIError(code="request_validation_error", message=exc.errors()).dict(),
    )


@app.exception_handler(APIException)
def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(code=exc.code, message=exc.message).dict(),
    )


@app.exception_handler(OAuth2Exception)
def oauth2_exception_handler(request: Request, exc: OAuth2Exception):
    return JSONResponse(
        status_code=exc.status_code,
        content=OAuth2Error(
            error_code=exc.code, error_description=exc.description
        ).dict(),
    )
