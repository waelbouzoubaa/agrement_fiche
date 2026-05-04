import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from lib.db import Base


def _id():
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"
    id = Column(String(36), primary_key=True, default=_id)
    name = Column(String(500), nullable=False)
    conducteur = Column(String(200), nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now())
    agrements = relationship(
        "Agrement", back_populates="project",
        cascade="all, delete-orphan",
        order_by="Agrement.number"
    )


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(String(36), primary_key=True, default=_id)
    name = Column(String(500), nullable=False)


class Product(Base):
    __tablename__ = "products"
    id = Column(String(36), primary_key=True, default=_id)
    designation = Column(String(500), nullable=False)
    category = Column(String(200), default="")
    supplier_name = Column(String(500), default="")
    datasheet_url = Column(String(500))  # blob GCS de la fiche technique produit


class Agrement(Base):
    __tablename__ = "agrements"
    id = Column(String(36), primary_key=True, default=_id)
    number = Column(Integer, nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    designation = Column(String(500), nullable=False)
    supplier_name = Column(String(500), nullable=False, default="")
    category = Column(String(200), default="")
    submitted_by = Column(String(200), default="")
    submitted_at = Column(DateTime)
    datasheet_path = Column(String(500))   # ancien champ local, conservé pour migration
    datasheet_url  = Column(String(500))   # blob GCS (ex: datasheets/abc123.pdf)
    status = Column(String(50), default="pending")
    project = relationship("Project", back_populates="agrements")
