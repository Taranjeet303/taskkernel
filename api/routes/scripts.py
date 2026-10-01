from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import ScriptCreate, ScriptResponse
from db.session import get_db
from models.models import Script


router = APIRouter()

@router.post("/scripts", response_model=ScriptResponse)
def create_script(
    script_create : ScriptCreate,
    db : Session = Depends(get_db)
):
    # 1.Create a script 
    script = Script(
        name=script_create.name,
        source=script_create.source

    )
    db.add(script)
    db.commit()
    db.refresh(script)

    return script



@router.get("/scripts", response_model=list[ScriptResponse])
def list_scripts(
    db : Session = Depends(get_db)
):
    scripts = db.query(Script).all()
    return scripts



@router.get("/scripts/{script_id}", response_model=ScriptResponse)
def get_script(
    script_id: UUID,
    db: Session = Depends(get_db)
):
    script = db.query(Script).filter(Script.id == script_id).first()

    if script is None:
        raise HTTPException(
            status_code=404,
            detail="Script not found"
        )

    return script

@router.delete("/scripts/{script_id}")
def delete_script(
    script_id: UUID,
    db: Session = Depends(get_db)
):
    script = db.query(Script).filter(Script.id == script_id).first()

    if script is None:
        raise HTTPException(
            status_code=404,
            detail="Script not found"
        )

    # Executions belong to the script, so deleting the script
    # also deletes its associated executions.
    db.delete(script)
    db.commit()

    return {
        "message": "Script deleted successfully"
    }

