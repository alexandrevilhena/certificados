from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Certificado(Base):
    __tablename__ = "certificados"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    curso = Column(String)
    data_conclusao = Column(Date)
    status = Column(String, default="PENDENTE")
