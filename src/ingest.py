import os
import glob
import pymupdf4llm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def process_pdfs():
    print(" Starting Phase 3 Local CTI Document Ingestion...")
    
    # 1. Absolute Path Setup
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    DB_DIR = os.path.join(DATA_DIR, "faiss_index")
    
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f" No PDFs found in: {DATA_DIR}")
        return

    print(f" Found {len(pdf_files)} PDFs. Extracting Markdown and chunking...")
    
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # 2. Extract & Chunk Phase
    for i, pdf_path in enumerate(pdf_files):
        filename = os.path.basename(pdf_path)
        print(f"   -> Processing [{i+1}/{len(pdf_files)}]: {filename}")
        try:
            md_text = pymupdf4llm.to_markdown(pdf_path)
            chunks = text_splitter.split_text(md_text)
            
            for chunk in chunks:
                all_chunks.append(Document(page_content=chunk, metadata={"source": filename}))
        except Exception as e:
            print(f"   Error processing {filename}: {e}")

    print(f"\n Extraction Complete. Total vector chunks created: {len(all_chunks)}")
    print(" Initiating Local HuggingFace Embedding Phase (BGE-Large)...")
    
    # 3. Local Embed & Store Phase (No API Limits!)
    # We use BAAI/bge-large-en-v1.5, one of the highest-rated open-source RAG models
    embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5", 
    model_kwargs={'device': 'mps'}
    )
    
    print("   -> Vectorizing chunks using your Mac's CPU/RAM. This may take a few minutes...")
    vector_store = FAISS.from_documents(all_chunks, embeddings)
            
    # 4. Save Database Phase
    print("\n Saving local FAISS database...")
    vector_store.save_local(DB_DIR)
    print(f" Success! Unrestricted local FAISS index built and saved to: {DB_DIR}")

if __name__ == "__main__":
    process_pdfs()