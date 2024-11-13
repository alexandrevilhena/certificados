from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import Certificado
from producer import publish_message

app = FastAPI()

Base.metadata.create_all(bind=engine)

class CertificadoRequest(BaseModel):
    nome: str
    curso: str
    data_conclusao: str

@app.post("/certificados/")
async def criar_certificado(request: CertificadoRequest, db: Session = Depends(get_db)):
    novo_certificado = Certificado(**request.dict())
    db.add(novo_certificado)
    db.commit()
    db.refresh(novo_certificado)

    await publish_message(novo_certificado.id)

    return {"mensagem": "Certificado solicitado com sucesso", "id": novo_certificado.id}

@app.get("/")
def read_root():
    return {"message": "API funcionando!"}
