import os
import re
import shutil
import chromadb
import ollama
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Set
from etl_pipeline import process_pdf_by_page, load_to_chroma
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

# --- 1. Initialize FastAPI & Middleware ---
app = FastAPI(
    title="AI Knowledge Assistant",
    description="Dynamic RAG-based API for analyzing uploaded documents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory if it doesn't exist
if not os.path.exists("./data"):
    os.makedirs("./data")

# --- 2. Database Connection ---
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="robotics_data")

# --- 3. Utilities (Required for /upload) ---
def clean_text(text):
    """Basic cleaning for OCR/PDF text."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, chunk_size=800, overlap=100):
    """Splits text into overlapping chunks for better context."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks

# --- 4. Data Models ---
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    source: str
    is_technical: bool
    distance: float
    pages: List[int]

# --- 5. Endpoints ---

@app.get("/")
async def serve_ui():
    return FileResponse("index.html")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Dynamically processes and indexes a PDF."""
    try:
        temp_path = f"./data/{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the PDF page-by-page
        for page_layout in extract_pages(temp_path):
            page_text = ""
            page_num = page_layout.pageid
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text += element.get_text()
            
            cleaned = clean_text(page_text)
            if cleaned:
                chunks = chunk_text(cleaned)
                for i, chunk in enumerate(chunks):
                    # Indexing directly into ChromaDB
                    collection.upsert(
                        documents=[chunk],
                        metadatas=[{"source": file.filename, "page": page_num}],
                        ids=[f"{file.filename}_p{page_num}_{i}"]
                    )

        return {"message": f"Successfully indexed {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reset")
async def reset_database():
    try:
        global collection
        client.delete_collection("robotics_data")
        collection = client.get_or_create_collection(name="robotics_data")
        
        # Also clean up the data directory
        data_dir = "./data"
        if os.path.exists(data_dir):
            for f in os.listdir(data_dir):
                os.path.join(data_dir, f)
                os.remove(os.path.join(data_dir, f))
                
        return {"status": "success", "message": "Database and file storage cleared."}
    except Exception as e:
        print(f"Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=ChatResponse)
async def ask_general_ai(request: ChatRequest):
    """Retrieves context and generates an answer."""
    try:
        results = collection.query(query_texts=[request.query], n_results=3)
        context_text = ""
        relevant_found = False
        source_name = "General Knowledge"
        best_distance = 2.0
        found_pages = set()
        
        if results['documents'] and results['documents'][0]:
            best_distance = results['distances'][0][0]
            for i in range(len(results['distances'][0])):
                if results['distances'][0][i] < 1.2: # Distance threshold
                    relevant_found = True
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    p_num = metadata.get('page', 0)
                    if p_num: found_pages.add(p_num)
                    context_text += f"\n[Document Context]: {content}\n"
                    source_name = metadata.get('source', 'Uploaded Document')

        if relevant_found:
            system_role = "You are a professional AI Assistant. Your tone and expertise must strictly match the provided context."
            final_prompt = f"CONTEXT:\n{context_text}\n\nQUESTION: {request.query}\n(Answer in the same language as the user)."
            source_name = f"{source_name} (Pages: {', '.join(map(str, sorted(list(found_pages))))})"
        else:
            system_role = "You are a helpful and polite General AI Assistant."
            final_prompt = f"Answer in the same language as the query: {request.query}"

        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'system', 'content': system_role}, {'role': 'user', 'content': final_prompt}]
        )
        
        return ChatResponse(
            answer=response['message']['content'],
            source=source_name,
            is_technical=relevant_found,
            distance=float(best_distance),
            pages=sorted(list(found_pages))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))