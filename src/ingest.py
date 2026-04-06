import os
import glob
import pymupdf4llm
import time
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Configuration
DATA_DIR = "./data"
DB_DIR = "./faiss_index"

def process_pdfs():
    print("Starting Advanced CTI Document Ingestion...")
    
    # Grab all PDFs in the data folder
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    if not pdf_files:
        print("No PDFs found in the 'data' folder!")
        return

    all_documents = []

    # 2. Advanced Extraction (Markdown Preservation)
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"Extracting markdown from: {filename}")
        
        # This magically converts the PDF into Markdown, preserving IOC tables!
        md_text = pymupdf4llm.to_markdown(pdf_path)
        
        # Store it as a LangChain Document with metadata for tracking
        doc = Document(
            page_content=md_text,
            metadata={"source": filename}
        )
        all_documents.append(doc)

    # 3. Intelligent Chunking
    # 1000 characters with a 200 character (20%) overlap to prevent cutting IPs in half
    print("\nChunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "|", " ", ""] # Respects markdown tables ("|")
    )
    
    chunks = text_splitter.split_documents(all_documents)
    print(f"Created {len(chunks)} contextual chunks.")

    # 4. Vectorization and FAISS Storage (WITH RATE LIMITING)
    print("\n Generating Google text embeddings in batches (to respect Free Tier limits)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")    
    # Process in batches of 50 to stay safely under the 100 requests/minute limit
    BATCH_SIZE = 50
    vector_store = None

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        print(f"   -> Processing batch {i // BATCH_SIZE + 1} (Chunks {i} to {i + len(batch)})...")
        
        # If it's the first batch, create the database
        if vector_store is None:
            vector_store = FAISS.from_documents(batch, embeddings)
        # For all subsequent batches, add to the existing database
        else:
            vector_store.add_documents(batch)
            
        # If there are more chunks left to process, pause for 30 seconds
        if i + BATCH_SIZE < len(chunks):
            print(" Pausing for 30 seconds to respect API rate limits...")
            time.sleep(30)
    
    # Save the completed database locally
    vector_store.save_local(DB_DIR)
    print(f"\n Success! FAISS vector database saved to '{DB_DIR}'.")

if __name__ == "__main__":
    # Ensure the API key is set
    if "GOOGLE_API_KEY" not in os.environ:
        print("ERROR: GOOGLE_API_KEY environment variable not found.")
        print("Please set it using: export GOOGLE_API_KEY='your_key'")
    else:
        process_pdfs()