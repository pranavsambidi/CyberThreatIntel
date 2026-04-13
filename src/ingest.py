import os
import glob
import time
import pymupdf4llm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def process_pdfs():
    print("Starting Advanced CTI Document Ingestion...")
    
    # 1. Absolute Path Setup
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    DB_DIR = os.path.join(DATA_DIR, "faiss_index")
    
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in: {DATA_DIR}")
        return

    print(f"Found {len(pdf_files)} PDFs. Extracting Markdown and chunking...")
    
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # 2. Extract & Chunk Phase
    for i, pdf_path in enumerate(pdf_files):
        filename = os.path.basename(pdf_path)
        print(f"   -> Processing [{i+1}/{len(pdf_files)}]: {filename}")
        try:
            # Extract raw Markdown to preserve IOC tables
            md_text = pymupdf4llm.to_markdown(pdf_path)
            chunks = text_splitter.split_text(md_text)
            
            # Wrap chunks in Document objects with source metadata
            for chunk in chunks:
                all_chunks.append(Document(page_content=chunk, metadata={"source": filename}))
        except Exception as e:
            print(f"   Error processing {filename}: {e}")

    print(f"\nExtraction Complete. Total vector chunks created: {len(all_chunks)}")
    print("Initiating Google Gemini Embedding Phase...")
    
    # 3. Embed & Store Phase (with Rate Limiting)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = None
    
    BATCH_SIZE = 50 # Process 50 chunks at a time
    
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i : i + BATCH_SIZE]
        current_batch = (i // BATCH_SIZE) + 1
        total_batches = (len(all_chunks) // BATCH_SIZE) + 1
        
        print(f"   -> Sending batch {current_batch}/{total_batches} to Gemini API...")
        
        if vector_store is None:
            vector_store = FAISS.from_documents(batch, embeddings)
        else:
            vector_store.add_documents(batch)
            
        # If we have more chunks left, sleep to prevent "Resource Exhausted" API errors
        if i + BATCH_SIZE < len(all_chunks):
            print("   Sleeping for 30 seconds to respect API rate limits...")
            time.sleep(30)
            
    # 4. Save Database Phase
    print("\nSaving local FAISS database...")
    vector_store.save_local(DB_DIR)
    print(f"Success! Massive FAISS index built and saved to: {DB_DIR}")

# This ensures the function runs when you execute the script
if __name__ == "__main__":
    process_pdfs()