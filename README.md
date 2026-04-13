# Cyber Threat Intel

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-gray.svg)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4.svg)

## Project Overview
Cyber Threat Intel is an enterprise-grade, hybrid Retrieval-Augmented Generation (RAG) pipeline designed for Security Operations Centers (SOC). The system ingests unstructured, highly technical Cyber Threat Intelligence (CTI) advisories (such as CISA and Mandiant reports) and synthesizes actionable intelligence while completely mitigating Large Language Model (LLM) hallucinations.

## Key Features & Architecture
* **Spatial-Aware Ingestion:** Utilizes `pymupdf4llm` to extract PDF text into Markdown, preserving the complex multi-column tabular structures where vital network indicators are typically stored.
* **Hybrid Retrieval Index (FAISS + BM25):** Fuses dense semantic vectorization (`gemini-embedding-001`) with sparse lexical retrieval. This ensures the system understands abstract concepts (e.g., "lateral movement") while still being able to exact-match alphanumeric strings (e.g., "CVE-2023-4966" or cryptographic hashes).
* **Deterministic Generation:** Powered by `gemini-2.5-flash` with a strict `temperature=0.1` and parametric confinement prompting to enforce a zero-trust, 100% anti-hallucination guardrail.
* **Automated Artifact Extraction:** The Streamlit UI features a background Regular Expression (Regex) engine that actively scrapes the AI's output for IPs, SHA256 hashes, and CVEs, routing them to a sidebar for immediate firewall deployment.

## Repository Structure
```text
Cyber Threat Intel/
├── data/                  # Raw CISA PDF advisories & local faiss_index database
├── notebooks/             # Jupyter notebooks for testing and RAG metric evaluation
│   ├── setup.ipynb
│   └── evaluate_rag.ipynb
├── src/                   # Core backend pipeline
│   └── ingest.py          # Custom batch-processing vectorization script
├── ui/                    # Frontend application
│   └── app.py             # Streamlit dashboard interface
├── results/               # Exported CSVs containing inference latency and evaluation metrics
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Installation & Setup
1. **Clone this repository:**
   ```bash
   git clone [https://github.com/pranavsambidi/CyberThreatIntel.git](https://github.com/pranavsambidi/CyberThreatIntel.git)
   cd CyberThreatIntel
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Authenticate with Google Cloud:**
   You must provide a Gemini Developer API key to utilize the embedding and generation endpoints.
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

## Execution Guide

**Phase 1: Database Generation**
Run the ingestion script to parse the PDFs and build the FAISS/BM25 indexes. 
*Note: This script implements a 30-second batch-sleep architecture to comply with Google Cloud's 1,000-request daily API limits.*
```bash
python src/ingest.py
```

**Phase 2: Launch the SOC Dashboard**
Start the interactive Streamlit interface to query your threat database.
```bash
python -m streamlit run ui/app.py
```

**Phase 3: Run Evaluation Metrics**
To reproduce the evaluation metrics for inference latency and guardrail success rates:
```bash
python -m jupyter notebook
# Open notebooks/evaluate_rag.ipynb and run all cells
```

## Early Evaluation Results
* **Retrieval Accuracy:** The hybrid ensemble effectively retrieves exact alphanumeric strings that standard dense models typically miss.
* **Anti-Hallucination Guardrails:** Achieved a **100% pass rate** during intentional stress testing. When queried about fictional threat actors not present in the vector space, the system successfully chokes the LLM and forces an "Insufficient data" refusal.
* **Known Limitations:** The free-tier Google API quota heavily bottlenecks the initial ingestion of large PDF corpuses (75+ reports). 

## Future Work (Deliverable 3)
* Migrate the embedding architecture to a locally hosted open-source model (e.g., HuggingFace `BGE-Large-En-v1.5`) to completely bypass cloud API rate limits.
* Implement the RAGAS framework for programmatic, mathematical scoring of Contextual Precision and Answer Faithfulness.

## Author
**Pranav Reddy Sambidi** Master of Science in AI Systems| University of Florida  
[pr.sambidi@ufl.edu](mailto:pr.sambidi@ufl.edu)
```