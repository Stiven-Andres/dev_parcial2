from sqlalchemy.future import select
from sqlalchemy import update
from data.models import UsuarioSQL, EstadoUsuario, TaskSQL, EstadoTask
from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession



from data.models import UsuarioSQL


def remove_tzinfo(dt: Optional[datetime | str]) -> Optional[datetime]:
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)  # convierte string a datetime
    if isinstance(dt, datetime) and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt

async def create_user_sql(session: AsyncSession, usuario: UsuarioSQL):
    usuario.created_at = remove_tzinfo(usuario.created_at)
    usuario.updated_at = remove_tzinfo(usuario.updated_at)

    db_usuario = UsuarioSQL.model_validate(usuario, from_attributes=True)
    db_usuario.created_at = datetime.now()

    session.add(db_usuario)
    await session.commit()
    await session.refresh(db_usuario)

    return db_usuario

async def obtener_todos_los_usuarios(session: AsyncSession):
    query = select(UsuarioSQL)
    result = await session.execute(query)
    return result.scalars().all()

async def obtener_usuario_por_id(session: AsyncSession, usuario_id: int):
    query = select(UsuarioSQL).where(UsuarioSQL.id == usuario_id)
    result = await session.execute(query)
    usuario = result.scalar_one_or_none()
    return usuario

async def actualizar_estado_usuario(session: AsyncSession, usuario_id: int, nuevo_estado: EstadoUsuario):
    query = (
        update(UsuarioSQL)
        .where(UsuarioSQL.id == usuario_id)
        .values(estado=nuevo_estado, updated_at=datetime.now())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

async def hacer_usuario_premium(session: AsyncSession, usuario_id: int):
    stmt = (
        update(UsuarioSQL)
        .where(UsuarioSQL.id == usuario_id)
        .values(premiun=True)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()

    result = await session.execute(select(UsuarioSQL).where(UsuarioSQL.id == usuario_id))
    usuario = result.scalar_one_or_none()

    if usuario is None:
        raise NoResultFound(f"No se encontró el usuario con ID {usuario_id}")

    return usuario

async def obtener_usuarios_inactivos(session: AsyncSession):
    query = select(UsuarioSQL).where(UsuarioSQL.estado == EstadoUsuario.inactivo)
    result = await session.execute(query)
    return result.scalars().all()

async def obtener_usuarios_inactivos_y_premium(session: AsyncSession):
    query = select(UsuarioSQL).where(
        (UsuarioSQL.estado == EstadoUsuario.inactivo) and
        (UsuarioSQL.premiun == True)
    )
    result = await session.execute(query)
    return result.scalars().all()

async def crear_task_sql(session: AsyncSession, task: TaskSQL):
    task.created_at = remove_tzinfo(task.created_at)
    task.updated_at = remove_tzinfo(task.updated_at)

    db_task = TaskSQL.model_validate(task, from_attributes=True)
    db_task.created_at = datetime.utcnow()

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

async def obtener_todas_las_tasks(session: AsyncSession):
    query = select(TaskSQL)
    result = await session.execute(query)
    return result.scalars().all()

async def obtener_task_por_id(session: AsyncSession, task_id: int):
    return await session.get(TaskSQL, task_id)

async def actualizar_task(session: AsyncSession, task_id: int, nuevo_estado: EstadoTask):
    query = (
        update(TaskSQL)
        .where(TaskSQL.id == task_id)
        .values(estado=nuevo_estado, updated_at=datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

async def eliminar_task(session: AsyncSession, task_id: int):
    task = await session.get(TaskSQL, task_id)
    if not task:
        return None

    task.estado = EstadoTask.eliminada
    task.updated_at = datetime.utcnow()
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
