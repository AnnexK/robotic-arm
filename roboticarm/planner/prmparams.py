from typing import Any
from pydantic import BaseModel, Field, root_validator


class PRMParams(BaseModel):
    k: int = Field(1, gt=0)
    n: int = Field(1, gt=0)
    thresh: float = Field(1e-8, ge=0.0)

    @root_validator
    def check_k_is_not_greater_than_n(
            cls,
            values: dict[str, Any],
    ) -> dict[str, Any]:
        if values["k"] > values["n"]:
            raise ValueError("kmax is greater than nmax")
        return values
