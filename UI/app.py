import streamlit as st
import re
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import pandas as pd

# Load the API key from your .env file
load_dotenv()

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="Cyber Threat Intel | SOC Dashboard",
    page_icon="https://img.icons8.com/fluency/512/cyber-security.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .cve-badge {background-color: #ff4b4b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold;}
    .mitre-badge {background-color: #f5a623; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold;}
    .ip-badge {background-color: #1e88e5; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold;}
    .stChatInputContainer {padding-bottom: 20px;}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. THE REGEX EXTRACTION ENGINE
# ==========================================
def extract_iocs(text):
    """Scans LLM output for standard network artifacts."""
    return {
        "CVEs": set(re.findall(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE)),
        "MITRE_IDs": set(re.findall(r"T\d{4}(?:\.\d{3})?", text)),
        "IPv4": set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)),
        "SHA256": set(re.findall(r"\b[A-Fa-f0-9]{64}\b", text))
    }


# ==========================================
# 3. LIVE RAG PIPELINE SETUP
# ==========================================
@st.cache_resource(show_spinner=False)
def load_pipeline():
    # 1. Build an absolute, bulletproof path to the database
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # This gets the /ui/ folder
    DB_DIR = os.path.join(BASE_DIR, "..", "data", "faiss_index") # This builds /CTI/data/faiss_index/
    
    # 2. Load Embeddings and Database
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5", model_kwargs={'device': 'mps'})
    vector_store = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_kwargs={"k": 4}) 
    
    # 3. Load LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    
    return retriever, llm

retriever, llm = load_pipeline()


# ==========================================
# 4. SESSION STATE MANAGEMENT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "System Initialized. Vector Index loaded. How can I assist your investigation today?"}
    ]
    
if "master_iocs" not in st.session_state:
    st.session_state.master_iocs = {"CVEs": set(), "MITRE_IDs": set(), "IPv4": set(), "SHA256": set()}


# ==========================================
# 5. SIDEBAR: EXTRACTED INTELLIGENCE
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/512/cyber-security.png", width=80)
    st.title("Extracted Intelligence")
    st.caption("Active Session Artifacts")
    st.divider()
    
    iocs = st.session_state.master_iocs
    
    if iocs["CVEs"]:
        st.markdown("**Vulnerabilities (CVE)**")
        for cve in iocs["CVEs"]:
            st.markdown(f"<span class='cve-badge'>{cve}</span>", unsafe_allow_html=True)
        st.write("")
        
    if iocs["MITRE_IDs"]:
        st.markdown("**MITRE ATT&CK Tactics**")
        for mitre in iocs["MITRE_IDs"]:
            st.markdown(f"<span class='mitre-badge'>{mitre}</span>", unsafe_allow_html=True)
        st.write("")
        
    if iocs["IPv4"]:
        st.markdown("**Network Indicators (IPv4)**")
        for ip in iocs["IPv4"]:
            st.code(ip, language="text")
            
    if iocs["SHA256"]:
        st.markdown("**Payload Hashes (SHA-256)**")
        for filehash in iocs["SHA256"]:
            st.code(filehash, language="text")
            
    if not any(iocs.values()):
        st.info("No network artifacts detected in the current session.")

    # ... (Keep the IOC display code above this) ...
    
    st.divider()
    
    # NEW: Export to CSV Feature
    if any(iocs.values()):
        import pandas as pd
        
        # Flatten the IOC dictionary for the CSV
        csv_data = []
        for category, values in iocs.items():
            for val in values:
                csv_data.append({"Indicator_Type": category, "Value": val})
                
        df = pd.DataFrame(csv_data)
        csv_file = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="💾 Export IOCs to SIEM (CSV)",
            data=csv_file,
            file_name="cyberthreatintel_extracted_iocs.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()
    if st.button("🗑️ Clear Session Data", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Session cleared. Ready for new query."}]
        st.session_state.master_iocs = {"CVEs": set(), "MITRE_IDs": set(), "IPv4": set(), "SHA256": set()}
        st.rerun()


# ==========================================
# 6. MAIN CHAT INTERFACE
# ==========================================

# Use HTML to place a realistic 3D icon perfectly next to the title
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
        <img src="https://img.icons8.com/fluency/512/cyber-security.png" width="55">
        <h1 style="margin: 0; padding: 0;">Cyber Threat Intel Analyst Console</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("Query the private intelligence repository. Powered by local BGE-Large embeddings & Gemini 2.5 Flash.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a threat intelligence question... (e.g., 'What CVEs does Akira exploit?')"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing threat intelligence vectors..."):
            
            # --- REAL RAG EXECUTION ---
            # 1. Retrieve the real documents from your Mac
            docs = retriever.invoke(prompt)
            context = "\n\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get("source", "Unknown") for doc in docs]
            
            # 2. Ask the Gemini LLM
            system_prompt = f"Context: {context}\n\nQuestion: {prompt}\nAnswer ONLY using context. If the data is missing, say 'Insufficient data'."
            full_response = llm.invoke(system_prompt).content
            
            # 3. Format output (UPDATED FOR TRANSPARENCY)
            st.markdown(full_response) # Print the answer immediately
            
            # Create a slick expander for the citations
            with st.expander("🔍 View Retrieved Context & Sources"):
                st.markdown("**Documents Analyzed:**")
                for src in set(sources):
                    st.markdown(f"- `{src}`")
                
                st.divider()
                st.markdown("**Raw Database Chunks:**")
                # Show the exact paragraphs the FAISS database pulled
                for i, doc in enumerate(docs):
                    st.info(f"**Chunk {i+1} from {doc.metadata.get('source', 'Unknown')}:**\n\n{doc.page_content}")
            
            # 4. Extract real IOCs!
            new_iocs = extract_iocs(full_response)
            
            # 5. Update the master IOC dictionary
            for key in st.session_state.master_iocs.keys():
                st.session_state.master_iocs[key].update(new_iocs[key])
            
            # 6. Save response to history
            # We append the text sources here so they persist when you scroll up in the chat!
            source_text = "\n\n**Sources Analyzed:**\n" + "\n".join([f"* `{src}`" for src in set(sources)])
            final_display = full_response + source_text
            st.session_state.messages.append({"role": "assistant", "content": final_display})
            
            st.rerun()