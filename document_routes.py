import os
import pdfplumber

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document_model import Document
from app.models.user_model import User

from app.auth.rbac import get_current_user, role_required


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get("/")
def get_all_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    documents = db.query(Document).all()

    return documents


@router.get("/search/")
def search_documents(
    company_name: str = None,
    document_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Document)

    if company_name:

        query = query.filter(
            Document.company_name.ilike(f"%{company_name}%")
        )

    if document_type:

        query = query.filter(
            Document.document_type.ilike(f"%{document_type}%")
        )

    documents = query.all()

    return documents


@router.post("/upload")
async def upload_document(
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["admin", "analyst"])
    )
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    upload_folder = "uploads"

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(
        upload_folder,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        content = await file.read()

        buffer.write(content)

    extracted_text = ""

    try:

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    extracted_text += text + "\n"

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF Extraction Failed: {str(e)}"
        )

    new_document = Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        filename=file.filename,
        filepath=file_path,
        extracted_text=extracted_text,
        uploaded_by=current_user.username
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "message": "Document uploaded successfully",
        "document_id": new_document.id,
        "title": title,
        "company_name": company_name,
        "document_type": document_type,
        "uploaded_by": current_user.username
    }


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["admin"])
    )
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully"
    }