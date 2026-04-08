from fastapi import APIRouter
import numpy as np
import database
from auth import get_current_user
from document_service import model

router = APIRouter()

@router.post("/documents/upload")
def upload_document(title: str, company_name: str, document_type: str, token: str, created_at: str):
    username = get_current_user(token)

    if username is None:
        return {"message": "invalid token"}
    for user in database.users:
        if user["username"] == username:
            role_name = user["role"]
            for role in database.roles:
                if role["name"] == role_name:
                    if "upload" in role["permissions"]:
                        document = {
                            "id": len(database.documents) + 1,
                            "title": title,
                            "company_name": company_name,
                            "document_type": document_type,
                            "uploaded_by": username,
                            "created_at": "2026-04-05"
                        }
                        database.documents.append(document)
                        text = f"{title} is a {document_type} for {company_name}"
                        embedding = model.encode(text)
                        embedding = np.array([embedding]).astype("float32")
                        database.index.add(embedding)
                        database.doc_mapping.append(document)
                        return {"message": " Uploaded"}
                    else:
                        return {"message": "permission denied"}
            return {"message": " role not found"}
    return {"message": "user not found"}

@router.get("/documents")
def get_documents():
    return database.documents

@router.get("/documents/search")
def search_documents(company_name: str):
    result = []
    for doc in database.documents:
        if doc["company_name"] == company_name:
            result.append(doc)
    return result

@router.get("/documents/{doc_id}")
def get_document(doc_id: int):
    for doc in database.documents:
        if doc["id"] == doc_id:
            return doc
    return {"message": "document not found"}

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, token: str):
    username = get_current_user(token)

    if username is None:
        return {"message": "invalid token"}
    for user in database.users:
        if user["username"] == username:
            role_name = user["role"]
            for role in database.roles:
                if role["name"] == role_name:
                    if "delete" in role["permissions"]:
                        for doc in database.documents:
                            if doc["id"] == doc_id:
                                database.documents.remove(doc)
                                return {"message": "Document deleted"}
                        return {"message": "document not found"}
                    else:
                        return {"message": "permission denied"}
            return {"message": "role not found"}
    return {"message": "user not found"}
