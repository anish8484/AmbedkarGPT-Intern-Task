"""RAG Service for AmbedkarGPT - Shared service for both CLI and Web"""

from pathlib import Path
from typing import Dict, List, Optional
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging

logger = logging.getLogger(__name__)

# Configure paths
ROOT_DIR = Path(__file__).parent.parent
SPEECH_FILE = ROOT_DIR / "speech.txt"
CHROMA_DB_DIR = ROOT_DIR / "chroma_db"


class RAGService:
    """Singleton RAG service for question answering"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.vectorstore = None
            self.qa_chain = None
            self.embeddings = None
            self.initialized = False
    
    def initialize(self) -> Dict[str, str]:
        """Initialize the RAG pipeline"""
        if self.initialized:
            return {"status": "already_initialized", "message": "RAG service already initialized"}
        
        try:
            logger.info("Initializing RAG service...")
            
            # Check if speech file exists
            if not SPEECH_FILE.exists():
                raise FileNotFoundError(f"Speech file not found at {SPEECH_FILE}")
            
            # Load document
            logger.info(f"Loading speech from {SPEECH_FILE}")
            loader = TextLoader(str(SPEECH_FILE))
            documents = loader.load()
            
            # Split text into chunks
            logger.info("Splitting text into chunks")
            text_splitter = CharacterTextSplitter(
                chunk_size=200,
                chunk_overlap=50,
                separator=". "
            )
            texts = text_splitter.split_documents(documents)
            
            # Create embeddings
            logger.info("Loading HuggingFace embeddings")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Create or load vector store
            logger.info("Setting up ChromaDB vector store")
            if CHROMA_DB_DIR.exists():
                self.vectorstore = Chroma(
                    persist_directory=str(CHROMA_DB_DIR),
                    embedding_function=self.embeddings
                )
            else:
                self.vectorstore = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    persist_directory=str(CHROMA_DB_DIR)
                )
            
            # Initialize Ollama LLM
            logger.info("Initializing Ollama with Mistral")
            self.llm = OllamaLLM(
                model="mistral",
                temperature=0.7,
                base_url="http://localhost:11434"
            )
            
            # Create RAG chain
            logger.info("Creating RAG chain")
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            
            # Create prompt template
            template = """Answer the question based on the following context from Dr. B.R. Ambedkar's speech:

Context: {context}

Question: {question}

Answer: """
            self.prompt = ChatPromptTemplate.from_template(template)
            
            # Create chain
            def format_docs(docs):
                return "\\n\\n".join(doc.page_content for doc in docs)
            
            self.qa_chain = (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            self.initialized = True
            logger.info("RAG service initialized successfully")
            
            return {
                "status": "success",
                "message": "RAG service initialized successfully",
                "chunks_count": len(texts)
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    def ask_question(self, question: str) -> Dict:
        """Ask a question and get an answer"""
        if not self.initialized:
            raise RuntimeError("RAG service not initialized. Call initialize() first.")
        
        try:
            logger.info(f"Processing question: {question}")
            
            # Get source documents
            source_docs = self.retriever.invoke(question)
            
            # Get answer from chain
            answer = self.qa_chain.invoke(question)
            
            # Format sources
            sources = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in source_docs
            ]
            
            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "sources_count": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            raise
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            "initialized": self.initialized,
            "speech_file_exists": SPEECH_FILE.exists(),
            "vector_db_exists": CHROMA_DB_DIR.exists()
        }


# Global instance
rag_service = RAGService()
