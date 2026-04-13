import os
import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
# ==========================================
# 1. ADVANCED UI & REGEX ENGINE
# ==========================================
st.set_page_config(page_title="CTI Analyst Suite", page_icon="🛡️", layout="wide")

def extract_iocs(text):
    """Regex engine to pull hard indicators from the LLM's text."""
    iocs = {
        "CVEs": list(set(re.findall(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE))),
        "IP Addresses": list(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text))),
        "SHA256 Hashes": list(set(re.findall(r"\b[A-Fa-f0-9]{64}\b", text)))
    }
    return iocs

# ==========================================
# 2. RAG PIPELINE INITIALIZATION
# ==========================================
if "GOOGLE_API_KEY" not in os.environ:
    st.error("GOOGLE_API_KEY environment variable is not set. Please set it in your terminal.")
    st.stop()

@st.cache_resource
def load_rag_pipeline():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.load_local("./data/faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # 1. FAISS Retriever (Semantic Search - Great for concepts)
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # 2. BM25 Retriever (Keyword Search - Great for exact Hashes/IPs/CVEs)
    # We extract the raw chunks from FAISS to feed into the BM25 algorithm
    docs = list(vector_store.docstore._dict.values())
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = 5
    
    # 3. The Ensemble Fusion (50% Semantic / 50% Keyword)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever], 
        weights=[0.5, 0.5]
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    
    system_prompt = (
        "You are an expert Security Operations Center (SOC) Tier-3 Analyst. "
        "Use the provided context to answer the user's question accurately. "
        "CRITICAL RULE: If the answer is not explicitly found in the context, you must state EXACTLY: "
        "'Insufficient data in current intelligence library.' Do not hallucinate or use outside knowledge.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    # IMPORTANT: We are now passing the 'ensemble_retriever' instead of just FAISS!
    return create_retrieval_chain(ensemble_retriever, question_answer_chain)

rag_chain = load_rag_pipeline()

# ==========================================
# 3. DASHBOARD LAYOUT
# ==========================================
# Split the screen: 70% for chat, 30% for the IOC extraction sidebar
col_chat, col_sidebar = st.columns([7, 3])

with col_sidebar:
    st.markdown("### 🎯 Extracted Intelligence")
    st.markdown("Indicators of Compromise (IOCs) detected in the current response will appear here for easy export.")
    ioc_container = st.empty()

with col_chat:
    st.title("🛡️ Cyber Threat Intel ChatBot")
    st.markdown("Query the private intelligence repository. Powered by RAG & Gemini.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a threat intelligence question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching intelligence repository..."):
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]
                
                sources = set(doc.metadata.get("source", "Unknown PDF") for doc in response["context"])
                
                full_response = f"{answer}\n\n**Sources Analyzed:**\n"
                for source in sources:
                    full_response += f"- `{source}`\n"
                    
                st.markdown(full_response)
                
                # --- NEW: Run Regex extraction and update sidebar ---
                detected_iocs = extract_iocs(answer)
                with col_sidebar:
                    with ioc_container.container():
                        for ioc_type, items in detected_iocs.items():
                            if items:
                                st.success(f"**{ioc_type} ({len(items)})**")
                                for item in items:
                                    st.code(item)
                
        st.session_state.messages.append({"role": "assistant", "content": full_response})