import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .database import Base, engine
from . import models
from .routers import patients
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Patient Registration API",
    description="REST API used by the Voice AI Patient Registration System.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "data": None,
            "error": {
                "message": str(exc.detail)
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    messages = []

    for error in exc.errors():
        location = error.get("loc", [])

        field = (
            str(location[-1])
            if location
            else "request"
        )

        message = error.get(
            "msg",
            "Invalid value",
        )

        message = message.replace(
            "Value error, ",
            "",
        )

        messages.append(
            f"{field}: {message}"
        )

    return JSONResponse(
        status_code=422,
        content={
            "data": None,
            "error": {
                "message": "; ".join(messages)
            },
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logging.exception(
        "Unexpected server error"
    )

    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "message": "An unexpected server error occurred"
            },
        },
    )


@app.get("/")
def root():
    return {
        "data": {
            "message": "Patient Registration API is running"
        },
        "error": None,
    }


@app.get("/health")
def health():
    return {
        "data": {
            "status": "healthy"
        },
        "error": None,
    }