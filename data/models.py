from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict


class EstadoTask(str, Enum):
    pendiente = "Pendiente"
    en_progreso = "En Progreso"
    completada = "Completada"
    eliminada = "Eliminada"


class TaskSQL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descripcion: Optional[str] = None
    estado: EstadoTask = Field(default=EstadoTask.pendiente)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class EstadoUsuario(str, Enum):
    activo = "Activo"
    inactivo = "Inactivo"
    eliminado = "Eliminado"


class UsuarioSQL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=3, max_length=40)
    email: str = Field(min_length=10, max_length=40)
    estado: EstadoUsuario = Field(default=EstadoUsuario.activo)
    premiun: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

