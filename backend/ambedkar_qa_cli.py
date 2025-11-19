#!/usr/bin/env python3
"""
AmbedkarGPT CLI - Command-line Q&A system based on Dr. B.R. Ambedkar's speech
Author: AmbedkarGPT Team
"""

import os
import sys
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Configure paths
ROOT_DIR = Path(__file__).parent.parent
SPEECH_FILE = ROOT_DIR / "speech.txt"
CHROMA_DB_DIR = ROOT_DIR / "chroma_db"


class AmbedkarQA:
    """RAG-based Q&A system for Dr. Ambedkar's speech"""
    
    def __init__(self):
        self.vectorstore = None
        self.qa_chain = None
        
    def setup(self):
        """Initialize the RAG pipeline"""
        print("🔧 Setting up AmbedkarGPT...")
        
        # Step 1: Load the document
        print(f"📄 Loading speech from {SPEECH_FILE}...")
        if not SPEECH_FILE.exists():
            raise FileNotFoundError(f"Speech file not found at {SPEECH_FILE}")
        
        loader = TextLoader(str(SPEECH_FILE))
        documents = loader.load()
        print(f"✓ Loaded {len(documents)} document(s)")
        
        # Step 2: Split text into chunks
        print("✂️  Splitting text into chunks...")
        text_splitter = CharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50,
            separator=". "
        )
        texts = text_splitter.split_documents(documents)
        print(f"✓ Created {len(texts)} text chunks")
        
        # Step 3: Create embeddings
        print("🧠 Loading HuggingFace embeddings model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✓ Embeddings model loaded")
        
        # Step 4: Create vector store
        print("💾 Creating ChromaDB vector store...")
        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=str(CHROMA_DB_DIR)
        )
        print("✓ Vector store created")
        
        # Step 5: Initialize Ollama LLM
        print("🤖 Initializing Ollama with Mistral 7B...")
        self.llm = OllamaLLM(
            model="mistral",
            temperature=0.7
        )
        print("✓ LLM initialized")
        
        # Step 6: Create RAG chain
        print("⛓️  Creating RAG chain...")
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Create prompt template
        template = """Answer the question based on the following context from Dr. B.R. Ambedkar's speech:

Context: {context}

Question: {question}

Answer: """
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create chain
        def format_docs(docs):
            return "\\n\\n".join(doc.page_content for doc in docs)
        
        self.qa_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print("✓ QA chain ready")
        print("\n✅ AmbedkarGPT is ready!\n")
        
    def ask(self, question: str) -> dict:
        """Ask a question and get an answer"""
        if not self.qa_chain:
            raise RuntimeError("QA system not initialized. Call setup() first.")
        
        # Get source documents
        source_docs = self.retriever.invoke(question)
        
        # Get answer
        answer = self.qa_chain.invoke(question)
        
        return {
            "result": answer,
            "source_documents": source_docs
        }
    
    def interactive_mode(self):
        """Run in interactive CLI mode"""
        print("="*60)
        print("🙏 Welcome to AmbedkarGPT!")
        print("Ask questions about Dr. B.R. Ambedkar's speech on caste.")
        print("Type 'exit' or 'quit' to end the session.")
        print("="*60)
        print()
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using AmbedkarGPT!")
                    break
                
                if not question:
                    print("⚠️  Please enter a question.")
                    continue
                
                print("\n🔍 Searching and generating answer...\n")
                result = self.ask(question)
                
                print("💡 Answer:")
                print("-" * 60)
                print(result['result'])
                print("-" * 60)
                
                # Show source chunks (optional)
                if result.get('source_documents'):
                    print(f"\n📚 Retrieved {len(result['source_documents'])} relevant text chunks")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Exiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    try:
        qa_system = AmbedkarQA()
        qa_system.setup()
        qa_system.interactive_mode()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
