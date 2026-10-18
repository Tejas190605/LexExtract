from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    word_count: int = 0
    status: str = "uploaded"


class DocumentCreate(DocumentBase):
    user_id: int
    stored_filename: str
    file_hash: str
    extracted_text: Optional[str] = None
    pages_json: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    stored_filename: str
    file_type: str
    file_size: int
    file_hash: str
    page_count: Optional[int] = None
    word_count: int
    status: str
    uploaded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    word_count: int
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class PageContent(BaseModel):
    page_number: int
    text: str


class DocumentTextResponse(BaseModel):
    document_id: int
    filename: str
    page_count: Optional[int] = None
    word_count: int
    text: str
    pages: List[PageContent] = []

    model_config = ConfigDict(from_attributes=True)
