from pydantic import BaseModel, Field


class ACOParams(BaseModel):
    alpha: float = Field(1.0, ge=0.0)
    beta: float = Field(1.0, ge=0.0)
    phi: float = Field(1e-6, ge=0.0)
    rho: float = Field(0.25, ge=0.0, le=1.0)
    q: float = Field(1.0, gt=0.0)
    m: int = Field(1, gt=0)
    i: int = Field(1, gt=0)
    elite: float = Field(1.0, ge=0.0)
    limit: int = Field(0, ge=0)
