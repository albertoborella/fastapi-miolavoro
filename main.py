from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, SQLModel, Session, create_engine, select

class Company(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, ge=1)
    internal_code: int
    name: str
    address: str
    city: str
    category: str

class JobBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True, ge=1)

class Job(JobBase, table=True):
    internal_code: int  
    date: str
    exports: int | None = Field(default=0)
    tramsit_permits: int | None = Field(default=0)
    inspection_areas: str | None = Field(default='')
    water_samples: str | None = Field(default='')
    mip_control: str | None = Field(default='')
    plan_creha: bool | None
    meeting_managers: str | None = Field(default='')
    audit_haccp: str | None = Field(default='')

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()
app.title = 'API sobre trabajo realizado'
app.version = '0.0.1'

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Endpoints
@app.get('/trabajos/', tags=['Trabajos'])
def all_jobs(session: SessionDep) -> list[Job]:
    works = session.exec(select(Job)).all()
    return works

@app.post('/trabajos/', tags=['Trabajos'])
def create_job(job: Job, session: SessionDep) -> Job:
    session.add(job)
    session.commit()
    session.refresh(job)
    return job

@app.get('/trabajos/{job_id}', tags=['Trabajos'])
def read_job(job_id: int, session: SessionDep) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Registro de trabajo no encontrado')
    return job

@app.patch('/trabajos/{trabajo_id}', tags=['Trabajos'])
def update_job(trabajo_id: int, trabajo: Job, session: SessionDep):
    jobo_db = session.get(Job, trabajo_id)
    if not jobo_db:
        raise HTTPException(status_code=404, detail="Registro de trabajo inexistente")
    trabajo_data = trabajo.model_dump(exclude_unset=True)
    jobo_db.sqlmodel_update(trabajo_data)
    session.add(jobo_db)
    session.commit()
    session.refresh(jobo_db)
    return jobo_db

@app.delete('/trabajos/{job_id}', tags=['Trabajos'])
def delete_job(job_id: int, session: SessionDep):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Trabajo no encontrado en la db')
    session.delete(job)
    session.commit()
    return {'ok': 'Registro de trabajo eliminado'}

# @app.get('/trabajos/{codigo}', tags=['Trabajos'])
# def work_for_empresa(codigo: str):
#     return list(filter(lambda cod: cod[codigo] == codigo, Job))




