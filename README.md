# Cyber Threat Intel: Multimodal RAG for Threat Intelligence Synthesis

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![HuggingFace](https://img.shields.io/badge/HuggingFace-BGE_Large-F58025.svg)
![Apple Silicon](https://img.shields.io/badge/Hardware-Apple_MPS-silver.svg)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4.svg)

## Project Overview
**Cyber Threat Intel** is an enterprise-grade, hybrid Retrieval-Augmented Generation (RAG) pipeline engineered for Security Operations Centers (SOC). The system resolves the unstructured data bottleneck by ingesting highly technical Cyber Threat Intelligence (CTI) advisories (such as CISA and Mandiant PDF reports) and synthesizing actionable intelligence while deterministically mitigating Large Language Model (LLM) hallucinations.

## Key Features & Architecture
* **Hardware-Accelerated Local Vectorization:** Bypassed cloud API rate limits entirely by migrating to a locally hosted `BAAI/bge-large-en-v1.5` embedding model. Utilizing Apple Metal Performance Shaders (MPS), the system rapidly indexes dense vector spaces using unified memory.
* **Hybrid Retrieval Index (FAISS + BM25):** Fuses dense semantic vectorization with sparse lexical retrieval. This ensures the system comprehends abstract behaviors (e.g., "living off the land") while retaining the ability to exact-match critical alphanumeric strings (e.g., "CVE-2023-4966" or cryptographic hashes).
* **Automated IOC Extraction & SIEM Export:** A background Regular Expression (Regex) engine actively scrapes the AI's output for IPv4 addresses, SHA-256 hashes, CVEs, and MITRE ATT&CK codes. These are routed to dynamic Session State memory and can be exported as a CSV for immediate enterprise firewall deployment with one click.
* **Verifiable Contextual Transparency:** The UI features a "Show Your Work" interactive expander, rendering the exact raw text paragraphs and document citations retrieved by the database to combat analyst automation bias.
* **Deterministic Generation:** Powered by `gemini-2.5-flash` with a strict `temperature=0.1` and parametric confinement prompting to enforce a zero-trust architecture.

## Repository Structure
```text
Cyber Threat Intel/
├── data/                  # Raw CISA PDF advisories & local faiss_index database
├── notebooks/             # Jupyter notebooks for testing and RAG metric evaluation
│   ├── setup.ipynb
│   └── evaluate_rag.ipynb # RAGAS mathematical evaluation script
├── src/                   # Core backend pipeline
│   └── ingest.py          # Apple MPS hardware-accelerated vectorization script
├── ui/                    # Frontend application
│   └── app.py             # Streamlit analyst dashboard interface
├── results/               # Exported CSVs containing final RAGAS metrics
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
   You must provide a Gemini Developer API key to utilize the final generative synthesis endpoint.
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

## Execution Guide

**Phase 1: Database Generation (Local)**
Run the ingestion script to parse the PDFs and build the FAISS/BM25 indexes. Utilizing local HuggingFace embeddings via Apple MPS, this runs entirely on local hardware without API quota restrictions.
```bash
python src/ingest.py
```

**Phase 2: Launch the SOC Dashboard**
Start the interactive Streamlit interface to query your threat database.
```bash
python -m streamlit run ui/app.py
```

**Phase 3: Run RAGAS Evaluation Metrics**
To reproduce the mathematical evaluation metrics for hallucination mitigation:
```bash
python -m jupyter notebook
# Open notebooks/evaluate_rag.ipynb and run all cells
```

## Final Evaluation Results (RAGAS)
The architecture was subjected to rigorous, programmatic evaluation using the RAGAS framework, utilizing a secondary LLM as a mathematical "Judge":
* **Faithfulness Score (1.000):** Achieved perfect hallucination mitigation. The system exhibited zero hallucination deviation from the localized threat data, proving the efficacy of parametric confinement.
* **Context Precision (1.000):** Demonstrated perfect retrieval accuracy on highly explicit exact-match queries (e.g., CVE and Hash extraction).

## Issues and Limitations
* **Cloud Inference Latency:** While vectorization is handled locally, the final generative synthesis still relies on the Google Gemini API. Complex multi-document synthesis queries can experience high latency (20+ seconds) due to HTTP timeout windows. 
* **RAGAS Judge Timeouts:** Heavy programmatic evaluation via the RAGAS framework may trigger `TimeoutError` exceptions due to massive context payloads exceeding the free-tier grading LLM's timeout window.

## Author
**Pranav Reddy Sambidi**<br>
Master of Science in Artificial Intelligence Systems, University of Florida<br>
Email: [pr.sambidi@ufl.edu](mailto:pr.sambidi@ufl.edu)
```