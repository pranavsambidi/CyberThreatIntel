# 🛡️ Cyber Threat Intel (CTI)

## Description
An enterprise-grade hybrid search (Dense FAISS + Sparse BM25) Retrieval-Augmented Generation (RAG) pipeline. It allows SOC analysts to query unstructured PDF threat reports using Google's Gemini 2.5 Flash model and automatically extracts hard Indicators of Compromise (IOCs) via Regex.

## Dataset
The dataset consists of highly technical, unstructured Cyber Threat Intelligence (CTI) reports (PDF format) detailing Advanced Persistent Threat (APT) campaigns, gathered from OSINT sources and GitHub repositories.

## Installation & Setup
1. Clone this repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Mac/Linux) or `.\venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set your API Key: `export GOOGLE_API_KEY="your_key_here"`

## How to Run
*   **To run the Data Pipeline:** `python src/ingest.py`
*   **To run the Dashboard:** `python -m streamlit run ui/app.py`
*   **To run the Notebook:** Navigate to the `notebooks/` folder and run `jupyter notebook setup.ipynb`

## Author
[Pranav Reddy Sambidi] - [pr.sambidi@ufl.edu]