# 💼 Financial Document Management System with Semantic Analysis

A production-ready FastAPI application for managing financial documents with AI-powered semantic search, Role-Based Access Control (RBAC), and a full RAG (Retrieval-Augmented Generation) pipeline.

---

## 🚀 Features

- **JWT Authentication** — Secure register and login
- **Role-Based Access Control** — Admin, Analyst, Auditor, Client roles with granular permissions
- **Document Management** — Upload, retrieve, search, and delete financial PDFs
- **PDF Text Extraction** — Automatic text extraction using `pdfplumber`
- **RAG Pipeline** — Document chunking → Embeddings → ChromaDB vector storage
- **Semantic Search** — Query financial documents using natural language
- **Reranking** — CrossEncoder reranking (Top 20 → Top 5 most relevant results)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Vector DB | ChromaDB |
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| Auth | JWT (python-jose) + bcrypt |
| PDF Parsing | pdfplumber |

---

## 📁 Project Structure

```
Financial Document Management/
├── app/
│   ├── auth/
│   │   ├── auth_handler.py       # Password hashing & verification
│   │   ├── jwt_handler.py        # JWT token creation
│   │   └── rbac.py               # Role-based access control
│   ├── models/
│   │   ├── user_model.py         # User SQLAlchemy model
│   │   └── document_model.py     # Document SQLAlchemy model
│   ├── rag/
│   │   ├── chunker.py            # Text chunking
│   │   ├── embedding.py          # Sentence embeddings
│   │   ├── vector_db.py          # ChromaDB operations
│   │   └── reranker.py           # CrossEncoder reranking
│   ├── routes/
│   │   ├── auth_routes.py        # Register & login
│   │   ├── roles_routes.py       # Role management
│   │   ├── dashboard_routes.py   # Role dashboards
│   │   ├── document_routes.py    # Document CRUD
│   │   └── rag_routes.py         # RAG & semantic search
│   ├── schemas/
│   │   └── user_schema.py        # Pydantic schemas
│   ├── database.py               # DB connection & session
│   └── main.py                   # App entry point
├── uploads/                      # Uploaded PDF files
├── chroma_db/                    # ChromaDB persistent storage
├── .env                          # Environment variables
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/financial-document-management.git
cd financial-document-management
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost/financial_rag_db
```

### 5. Create the PostgreSQL database
```sql
CREATE DATABASE financial_rag_db;
```

### 6. Run the application
```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## 📦 Requirements

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-dotenv
python-multipart
pdfplumber
sentence-transformers
chromadb
langchain-text-splitters
pydantic[email]
```

---

## 🔑 API Reference

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register a new user | ❌ |
| POST | `/auth/login` | Login (returns JWT token) | ❌ |

### Roles & Permissions
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/roles/create` | Create a role | Admin |
| POST | `/users/assign-role` | Assign role to user | Admin |
| GET | `/users/{id}/roles` | Get user role | Admin |
| GET | `/users/{id}/permissions` | Get user permissions | Admin |

### Documents
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/documents/upload` | Upload a PDF document | Admin, Analyst |
| GET | `/documents/` | Get all documents | All |
| GET | `/documents/{id}` | Get document by ID | All |
| GET | `/documents/search/` | Search by company or type | All |
| DELETE | `/documents/{id}` | Delete a document | Admin |

### RAG
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/rag/index-document/{id}` | Chunk, embed & store in ChromaDB | Admin, Analyst |
| DELETE | `/rag/remove-document/{id}` | Remove document embeddings | Admin |
| POST | `/rag/search` | Semantic search with reranking | All |
| GET | `/rag/context/{id}` | Get all chunks for a document | All |

### Dashboards
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/admin/dashboard` | Admin dashboard | Admin |
| GET | `/analyst/dashboard` | Analyst dashboard | Admin, Analyst |
| GET | `/client/dashboard` | Client dashboard | Client |
| GET | `/auditor/dashboard` | Auditor dashboard | Auditor |

---

## 🔄 RAG Pipeline

```
PDF Upload
    ↓
Text Extraction (pdfplumber)
    ↓
Chunking (LangChain RecursiveCharacterTextSplitter)
    ↓
Embeddings (all-MiniLM-L6-v2)
    ↓
Vector Storage (ChromaDB)
    ↓
User Query → Embed → Vector Search (Top 20)
    ↓
CrossEncoder Reranking
    ↓
Top 5 Most Relevant Results
```

---

## 👤 Role Permissions

| Permission | Admin | Analyst | Auditor | Client |
|------------|-------|---------|---------|--------|
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Assign Roles | ✅ | ❌ | ❌ | ❌ |
| Upload Documents | ✅ | ✅ | ❌ | ❌ |
| Delete Documents | ✅ | ❌ | ❌ | ❌ |
| Edit Documents | ✅ | ✅ | ❌ | ❌ |
| Review Documents | ✅ | ❌ | ✅ | ❌ |
| View Documents | ✅ | ✅ | ✅ | ✅ |
| Semantic Search | ✅ | ✅ | ✅ | ✅ |

---

## 🧪 Usage Example

### 1. Register & Login
```bash
# Register
POST /auth/register
{
  "username": "vinay",
  "email": "vinay@gmail.com",
  "password": "Vinay@1206"
}

# Login — use email or username in the username field
POST /auth/login
username: vinay@gmail.com
password: Vinay@1206
```

### 2. Authorize in Swagger
Click the **🔒 Authorize** button → paste:
```
Bearer <your_access_token>
```

### 3. Upload & Index a Document
```bash
POST /documents/upload   # upload PDF
POST /rag/index-document/1  # index document with id=1
```

### 4. Semantic Search
```bash
POST /rag/search
query: "What is the revenue for Q3 2025?"
```

---

## 📄 License

This project was built as part of the Nimap AI & ML Assignment.
