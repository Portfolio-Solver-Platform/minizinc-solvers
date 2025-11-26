from fastapi import APIRouter
from psp_solver_sdk.config import SolverConfig
from pydantic import BaseModel, Field


class VersionResponse(BaseModel):
    service: str = Field(..., description="Name of the service")
    version: str = Field(
        ..., description="Semantic version of the service implementation"
    )
    api_version: str = Field(
        ..., description="API contract version exposed by the service"
    )


def router(config: SolverConfig) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/version",
        response_model=VersionResponse,
        summary="Get information about the service",
    )
    def version():
        """
        Get information about the service.
        """
        return VersionResponse(
            service=config.service.name,
            version=config.service.version,
            api_version=config.api.version,
        )

    return router
