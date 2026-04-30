import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from lib.models import Project, Supplier, Product, Agrement


def _id():
    return str(uuid.uuid4())


# ── Helpers ──────────────────────────────────────────────────────────────────

def _project_dict(p: Project) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "conducteur": p.conducteur,
        "created_at": p.created_at,
        "agrement_count": len(p.agrements),
    }


def _agrement_dict(a: Agrement) -> dict:
    return {
        "id": a.id,
        "number": a.number,
        "designation": a.designation,
        "supplier_name": a.supplier_name,
        "category": a.category or "",
        "submitted_by": a.submitted_by or "",
        "submitted_at": a.submitted_at,
        "datasheet_path": a.datasheet_path,
        "status": a.status or "pending",
        "project_id": a.project_id,
    }


# ── Projects ──────────────────────────────────────────────────────────────────

def get_projects(db: Session) -> list[dict]:
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return [_project_dict(p) for p in projects]


def get_project(db: Session, project_id: str) -> dict | None:
    p = db.query(Project).filter(Project.id == project_id).first()
    return _project_dict(p) if p else None


def create_project(db: Session, name: str, conducteur: str) -> dict:
    p = Project(id=_id(), name=name, conducteur=conducteur)
    db.add(p)
    db.flush()
    return _project_dict(p)


def delete_project(db: Session, project_id: str):
    p = db.query(Project).filter(Project.id == project_id).first()
    if p:
        db.delete(p)


# ── Suppliers ─────────────────────────────────────────────────────────────────

def get_suppliers(db: Session, q: str = "") -> list[dict]:
    query = db.query(Supplier)
    if q:
        query = query.filter(Supplier.name.ilike(f"%{q}%"))
    return [{"id": s.id, "name": s.name} for s in query.order_by(Supplier.name).all()]


def create_supplier(db: Session, name: str) -> dict:
    existing = db.query(Supplier).filter(Supplier.name == name).first()
    if existing:
        return {"id": existing.id, "name": existing.name}
    s = Supplier(id=_id(), name=name)
    db.add(s)
    db.flush()
    return {"id": s.id, "name": s.name}


def delete_supplier(db: Session, supplier_id: str):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if s:
        db.delete(s)


# ── Products ──────────────────────────────────────────────────────────────────

def get_products(db: Session, q: str = "") -> list[dict]:
    query = db.query(Product)
    if q:
        query = query.filter(Product.designation.ilike(f"%{q}%"))
    return [
        {"id": p.id, "designation": p.designation,
         "supplier_name": p.supplier_name, "category": p.category or ""}
        for p in query.order_by(Product.designation).all()
    ]


def create_product(db: Session, designation: str, supplier_name: str, category: str) -> dict:
    p = Product(id=_id(), designation=designation, supplier_name=supplier_name, category=category)
    db.add(p)
    db.flush()
    return {"id": p.id, "designation": p.designation,
            "supplier_name": p.supplier_name, "category": p.category}


def delete_product(db: Session, product_id: str):
    p = db.query(Product).filter(Product.id == product_id).first()
    if p:
        db.delete(p)


# ── Agrements ─────────────────────────────────────────────────────────────────

def get_agrements(db: Session, project_id: str) -> list[dict]:
    agrements = (
        db.query(Agrement)
        .filter(Agrement.project_id == project_id)
        .order_by(Agrement.number)
        .all()
    )
    return [_agrement_dict(a) for a in agrements]


def create_agrement(
    db: Session, project_id: str, number: int, designation: str,
    supplier_name: str, category: str, submitted_by: str,
    submitted_at: datetime
) -> dict:
    a = Agrement(
        id=_id(),
        number=number,
        project_id=project_id,
        designation=designation,
        supplier_name=supplier_name,
        category=category,
        submitted_by=submitted_by,
        submitted_at=submitted_at,
    )
    db.add(a)
    # Ensure supplier and product exist for future autocomplete
    _ensure_supplier(db, supplier_name)
    _ensure_product(db, designation, supplier_name, category)
    db.flush()
    return _agrement_dict(a)


def update_agrement_datasheet(db: Session, agrement_id: str, path: str | None) -> dict | None:
    a = db.query(Agrement).filter(Agrement.id == agrement_id).first()
    if a:
        a.datasheet_path = path
        db.flush()
        return _agrement_dict(a)
    return None


def delete_agrement(db: Session, agrement_id: str):
    a = db.query(Agrement).filter(Agrement.id == agrement_id).first()
    if a:
        db.delete(a)


def _ensure_supplier(db: Session, name: str):
    if name and not db.query(Supplier).filter(Supplier.name == name).first():
        db.add(Supplier(id=_id(), name=name))


def _ensure_product(db: Session, designation: str, supplier_name: str, category: str):
    if not db.query(Product).filter(
        Product.designation == designation,
        Product.supplier_name == supplier_name
    ).first():
        db.add(Product(id=_id(), designation=designation,
                       supplier_name=supplier_name, category=category))
