from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    extracted_text = Column(Text)
    uploaded_by = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String, nullable=False)
    company_name = Column(String)
    document_type = Column(String)
