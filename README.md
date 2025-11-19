# AmbedkarGPT - AI-Powered Q&A System

An intelligent question-answering system based on Dr. B.R. Ambedkar's speech "Annihilation of Caste" using RAG (Retrieval-Augmented Generation) technology.

## 🌟 Features

- **CLI Interface**: Command-line Q&A system for terminal users
- **Web Interface**: Beautiful React-based web UI for easy interaction
- **RAG Pipeline**: Uses LangChain, ChromaDB, and Ollama for accurate answers
- **Local & Free**: Runs 100% locally with no API keys required
- **Source Attribution**: Shows retrieved text chunks for transparency

## 🏗️ Architecture

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Question │
    └────┬─────┘
         │
┌────────▼────────────┐
│  Text Embedding     │
│  (HuggingFace)      │
└────────┬────────────┘
         │
┌────────▼────────────┐
│  Vector Search      │
│  (ChromaDB)         │
└────────┬────────────┘
         │
┌────────▼────────────┐
│  Context + Query    │
│  → LLM (Mistral)    │
└────────┬────────────┘
         │
    ┌────▼─────┐
    │  Answer  │
    └──────────┘
```

## 🛠️ Tech Stack

- **Framework**: LangChain (RAG orchestration)
- **Vector Database**: ChromaDB (local vector storage)
- **Embeddings**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **LLM**: Ollama with Mistral 7B
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 19 + Shadcn UI + Tailwind CSS
- **Database**: MongoDB (for conversation history)

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16+ (for web interface)
- Ollama installed and running
- 8GB+ RAM recommended

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### 2. Pull Mistral Model

```bash
ollama pull mistral
```

### 3. Start Ollama Server

```bash
ollama serve
```

### 4. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Run CLI Interface

```bash
cd backend
python ambedkar_qa_cli.py
```

### 6. Run Web Interface (Optional)

**Backend:**
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```bash
cd frontend
yarn install
yarn start
```

Visit: `http://localhost:3000`

## 💻 CLI Usage

```bash
python backend/ambedkar_qa_cli.py
```

**Example interaction:**
```
🙏 Welcome to AmbedkarGPT!
Ask questions about Dr. B.R. Ambedkar's speech on caste.
Type 'exit' or 'quit' to end the session.
============================================================

❓ Your question: What is the real remedy according to Dr. Ambedkar?

🔍 Searching and generating answer...

💡 Answer:
------------------------------------------------------------
According to Dr. Ambedkar, the real remedy is to destroy the 
belief in the sanctity of the shastras. He argues that as long 
as people continue to hold the shastras as sacred and infallible, 
they will never be able to eliminate the caste system.
------------------------------------------------------------

📚 Retrieved 3 relevant text chunks
```

## 🌐 Web Interface

The web interface provides:
- Clean, modern UI with gradient backgrounds
- Real-time Q&A interaction
- Sample questions to get started
- Source document display
- Conversation history
- Loading states and error handling

**Sample Questions:**
- What is the real remedy according to Dr. Ambedkar?
- What does Dr. Ambedkar say about the shastras?
- How does Dr. Ambedkar compare social reform to gardening?
- What is the real enemy according to this speech?

## 📁 Project Structure

```
.
├── backend/
│   ├── server.py              # FastAPI server
│   ├── rag_service.py         # RAG service (shared)
│   ├── ambedkar_qa_cli.py     # CLI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styles
│   │   └── components/       # UI components
│   ├── package.json          # Node dependencies
│   └── public/               # Static files
├── speech.txt                # Dr. Ambedkar's speech
├── chroma_db/                # Vector database (auto-created)
└── README.md                 # This file
```

## 🔧 API Endpoints

### Initialize RAG Service
```http
POST /api/ambedkar/init
```

**Response:**
```json
{
  "status": "success",
  "message": "RAG service initialized successfully",
  "chunks_count": 8
}
```

### Check Status
```http
GET /api/ambedkar/status
```

**Response:**
```json
{
  "initialized": true,
  "speech_file_exists": true,
  "vector_db_exists": true
}
```

### Ask Question
```http
POST /api/ambedkar/ask
Content-Type: application/json

{
  "question": "What is the real remedy?"
}
```

**Response:**
```json
{
  "question": "What is the real remedy?",
  "answer": "According to Dr. Ambedkar, the real remedy is to destroy the belief in the sanctity of the shastras...",
  "sources": [
    {
      "content": "The real remedy is to destroy the belief...",
      "metadata": {}
    }
  ],
  "sources_count": 3
}
```

## 🧪 Testing

### Test CLI
```bash
cd backend
python -c "from rag_service import rag_service; rag_service.initialize(); print(rag_service.ask_question('What is the real remedy?'))"
```

### Test API
```bash
# Initialize
curl -X POST http://localhost:8001/api/ambedkar/init

# Ask Question
curl -X POST http://localhost:8001/api/ambedkar/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the real remedy?"}'
```

## 🎨 Customization

### Adjust Text Chunking
Edit `rag_service.py`:
```python
text_splitter = CharacterTextSplitter(
    chunk_size=200,      # Increase for larger chunks
    chunk_overlap=50,    # Increase for more overlap
    separator=". "
)
```

### Change LLM Model
```python
llm = OllamaLLM(
    model="mistral",     # Try: llama2, codellama, etc.
    temperature=0.7      # 0.0 = deterministic, 1.0 = creative
)
```

### Modify Retrieval
```python
retriever=self.vectorstore.as_retriever(
    search_kwargs={"k": 3}  # Number of chunks to retrieve
)
```

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Model Not Found
```bash
# Pull Mistral model
ollama pull mistral

# List available models
ollama list
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade langchain langchain-community chromadb sentence-transformers langchain-ollama
```

### ChromaDB Errors
```bash
# Delete and reinitialize vector database
rm -rf chroma_db/
python -c "from rag_service import rag_service; rag_service.initialize()"
```

## 📝 About the Speech

The text used in this project is an excerpt from Dr. B.R. Ambedkar's seminal work **"Annihilation of Caste"** (1936), which critiques the caste system and Hindu scriptures' role in perpetuating social inequality.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open-source and available under the MIT License.

## 👤 Author

**AmbedkarGPT Team**
- GitHub: [AmbedkarGPT-Intern-Task](https://github.com/yourusername/AmbedkarGPT-Intern-Task)

## 🙏 Acknowledgments

- Dr. B.R. Ambedkar for his profound insights
- LangChain team for the excellent framework
- Ollama for local LLM inference
- HuggingFace for embeddings models
- ChromaDB for vector storage

---

**Built with ❤️ for preserving and sharing Dr. Ambedkar's wisdom**
