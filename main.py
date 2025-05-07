from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Path
from utils.connection_db import *
from sqlmodel.ext.asyncio.session import AsyncSession
from data.models import UsuarioSQL, EstadoUsuario
from operations.operations_db import create_user_sql, obtener_todos_los_usuarios, obtener_usuario_por_id, actualizar_estado_usuario,hacer_usuario_premium, obtener_usuarios_inactivos, obtener_usuarios_inactivos_y_premium, crear_task_sql, obtener_todas_las_tasks, obtener_task_por_id, actualizar_task, eliminar_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa la BD antes de levantar el servidor
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "¡API en funcionamiento!"}

@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@router.post(
    "/usuarios/",
    response_model=UsuarioSQL,
    status_code=status.HTTP_201_CREATED
)
async def create_usuario(
    usuario: UsuarioSQL,
    session: AsyncSession = Depends(get_session)
):
    try:
        nuevo_usuario = await create_user_sql(session, usuario)
        return nuevo_usuario
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario: {str(e)}"
        )

@app.get("/usuarios/inactivos")
async def listar_usuarios_inactivos(session: AsyncSession = Depends(get_session)):
    return await obtener_usuarios_inactivos_y_premium(session)

@app.get("/usuarios/inactivos-premiun")
async def listar_usuarios_inactivos_premiun(session: AsyncSession = Depends(get_session)):
    return await obtener_usuarios_inactivos(session)

@app.get("/usuarios")
async def leer_usuarios(session: AsyncSession = Depends(get_session)):
    return await obtener_todos_los_usuarios(session)


@app.get("/usuarios/{usuario_id}")
async def leer_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    usuario = await obtener_usuario_por_id(session, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
app.include_router(router)

@app.put("/usuarios/{usuario_id}/estado")
async def actualizar_estado_usuario_endpoint(
    usuario_id: int,
    nuevo_estado: EstadoUsuario,
    session: AsyncSession = Depends(get_session)
):
    await actualizar_estado_usuario(session, usuario_id, nuevo_estado)
    return {"mensaje": f"Estado del usuario {usuario_id} actualizado a {nuevo_estado}"}

@app.put("/usuarios/{usuario_id}/premium")
async def hacer_premium(usuario_id: int, session: AsyncSession = Depends(get_session)):
    return await hacer_usuario_premium(session, usuario_id)

@app.post("/", response_model=TaskSQL)
async def crear_task_sql(task: TaskSQL, session: AsyncSession = Depends(get_session)):
    return await crear_task_sql(session, task)


@app.get("/", response_model=List[TaskSQL])
async def obtener_todas_las_tasks(session: AsyncSession = Depends(get_session)):
    return await obtener_todas_las_tasks(session)


@app.get("/{task_id}", response_model=TaskSQL)
async def obtener_task_por_id(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await obtener_task_por_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# UPDATE task
@app.put("/{task_id}", response_model=TaskSQL)
async def actualizar_task(task_id: int, task_data: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    task = await actualizar_task(session, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# DELETE (logical) task
@app.delete("/{task_id}", response_model=TaskSQL)
async def eliminar_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await eliminar_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task








