## Google Sheets Vector Store App

A minimal Streamlit application that:
1. Accepts Google Service Account credentials (JSON text)
2. Downloads a single Google Sheets document (all sheets)
3. Builds text chunks and embeddings (HuggingFace `BAAI/bge-small-en-v1.5`)
4. Stores them in a local ChromaDB persistent collection
5. Shows collection statistics

### ✨ Features
- One-click end‑to‑end pipeline (data -> embeddings -> vector store -> stats)
- No OpenAI key required (uses free HuggingFace embeddings)
- Automatic fallback manual reader if LlamaIndex reader returns zero docs
- Persistent local vector store under `./chroma_db`

### 🚀 Quick Start
```bash
git clone <your-repo-url>
cd google_sheets
python -m venv venv
venv\\Scripts\\activate  # Windows
# or: source venv/bin/activate  (Linux/Mac)
pip install -r requirements.txt
streamlit run main.py
```

### 🔐 Create Service Account
1. Open Google Cloud Console → APIs & Services → Credentials
2. Enable Google Sheets API (and Drive API if needed)
3. Create Service Account → create key (JSON) → download
4. Share your target Sheet with the service account email (Viewer)
5. Open the JSON file and paste its contents in the app

### ▶️ Usage
1. Paste credentials JSON
2. Enter the Sheet ID (from the URL `.../spreadsheets/d/<ID>/edit`)
3. Click "Start Process" – wait for success + stats

### � Current Project Structure
```
├── main.py                       # Streamlit UI + orchestration
├── downloader.py                 # Direct Google Sheets API downloader
├── google_sheets_embedding_method.py  # Document + fallback builder
├── vector_store_manager.py       # ChromaDB + embedding index
├── shared/
│   └── config.py                 # Environment setup
├── chroma_db/                    # Persistent Chroma storage
├── requirements.txt
└── README.md
```

### 🧠 Embedding / Chunking
- Chunk size: 1024 characters (SentenceSplitter)
- Overlap: 50 characters
- Model: `BAAI/bge-small-en-v1.5`

### 🗃️ Vector Store
- Backend: ChromaDB (persistent)
- Collection name pattern: `sheets_<sheet_id_prefix>`

### 🛠 Extending
- Add a query interface with similarity search
- Support multiple Sheets / batch mode
- Add deletion or re-index buttons

### 📄 License
MIT (add a LICENSE file if distributing publicly).

---
Feel free to open issues or suggest improvements.