import os
import re
import time
import logging
import functools
import chromadb
import ollama
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

# Suppress pdfminer logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# --- 1. Database Setup (Lazy/Optional) ---
# We do NOT initialize the client globally to avoid side effects on import
# client = chromadb.PersistentClient(path="./chroma_db")
# collection = client.get_or_create_collection(name="robotics_data")

# --- 2. Utilities ---
def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[{func.__name__}] processed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def clean_text(text):
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks

# --- 3. UPDATED ETL Functions (Page Tracking) ---

@log_time
def process_pdf_by_page(pdf_path):
    """Extracts text page-by-page to keep track of sources."""
    pages_data = []
    try:
        # We use extract_pages to get page layout objects
        for page_layout in extract_pages(pdf_path):
            page_text = ""
            # pageid starts from 1
            page_num = page_layout.pageid 
            
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text += element.get_text()
            
            cleaned = clean_text(page_text)
            if cleaned:
                pages_data.append({"text": cleaned, "page": page_num})
        return pages_data
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

def load_to_chroma(pages_data, filepath, collection):
    """Chunks each page and stores it with the page number in metadata."""
    filename = os.path.basename(filepath)
    all_chunks = []
    all_metadatas = []
    all_ids = []

    for item in pages_data:
        text = item["text"]
        page_num = item["page"]
        
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": filename,
                "page": page_num
            })
            all_ids.append(f"{filename}_p{page_num}_{i}")

    if all_chunks:
        collection.upsert(documents=all_chunks, metadatas=all_metadatas, ids=all_ids)
        print(f"✅ Loaded {len(all_chunks)} chunks with page metadata from {filename}.")
        return len(all_chunks)
    return 0

def chat_with_db(collection):
    print("\n" + "="*45)
    print("🤖 PRO AI ASSISTANT (V4.0 - CONTEXT AWARE)")
    print("Logic: Document Grounding + Page Citations")
    print("="*45 + "\n")

    session_history = [] 

    while True:
        try:
            user_input = input("Query: ").strip()
            if user_input.lower() in ('exit', 'quit'):
                print("Goodbye! 👋")
                break
            if not user_input: continue

            # A. RETRIEVAL STEP
            results = collection.query(query_texts=[user_input], n_results=3)
            context_text = ""
            relevant_found = False
            sources = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    if results['distances'][0][i] < 1.2: 
                        relevant_found = True
                        content = results['documents'][0][i]
                        page = results['metadatas'][0][i].get('page', '?')
                        
                        context_text += f"\n[From Page {page}]: {content}\n"
                        sources.append(f"Page {page}")

            # B. PROMPT AUGMENTATION
            if relevant_found:
                unique_pages = ", ".join(sorted(list(set(sources))))
                print(f"✅ Found technical data on: {unique_pages}")
                final_prompt = f"""Use the provided context to answer. 
                Reference the page numbers in your response if possible.
                Context: {context_text}
                Question: {user_input}"""
            else:
                print(f"💡 No PDF match. Replying generally...")
                final_prompt = f"You are a General AI Assistant. The user asks: {user_input}"

            # C. GENERATION STEP
            session_history.append({'role': 'user', 'content': final_prompt})
            
            try:
                print("\n📝 Assistant:")
                stream = ollama.chat(model='llama3', messages=session_history, stream=True)
                
                ai_response = ""
                for chunk in stream:
                    content = chunk['message']['content']
                    print(content, end='', flush=True)
                    ai_response += content
                print("\n")

                session_history.append({'role': 'assistant', 'content': ai_response})
                if len(session_history) > 6: session_history = session_history[-6:]

            except Exception as e:
                print(f"\n⚠️ Ollama Error: {e}")

        except KeyboardInterrupt:
            break

# --- 4. Main Execution ---
def main():
    # Initialize DB only when running as script
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="robotics_data")

    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Please put your PDFs in the '{data_dir}' folder.")
        # We don't return here if we want to chat even without new PDFs, 
        # but for ETL focus it's fine.
        
    pdf_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.pdf')]
    
    for pdf_path in pdf_files:
        print(f"\n📄 Processing: {pdf_path}")
        pages_data = process_pdf_by_page(pdf_path)
        if pages_data:
            load_to_chroma(pages_data, pdf_path, collection)
    
    chat_with_db(collection)

if __name__ == "__main__":
    main()