from pathlib import Path

from pydantic import BaseModel, Field, validator

from .types import Vector3, State


class TaskDataError(Exception):
    pass


class TaskData(BaseModel):
    urdf: Path = Field(alias="urdf_name")
    sdf: Path | None = Field(alias="sdf_name")
    effector: str = Field(alias="effector_name")
    target_pos: Vector3 = Field(alias="endpoint")
    pos: Vector3 = Field((.0, .0, .0))
    orn: Vector3 = Field((.0, .0, .0))
    fixed: bool = Field(True, alias="fixed_base")
    eps: float = Field(1e-4, ge=1e-6)
    init_state: State | None = Field(None, alias="dofs")

    @validator('urdf', 'sdf')
    def absolutize_paths(cls, value: Path) -> Path:
        return value.resolve().absolute()
