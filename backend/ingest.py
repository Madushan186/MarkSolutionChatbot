import csv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document

# 1. Load Data from CSV
documents = []
with open("sample_data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Combine question and answer for context
        text = f"Question: {row['question']}\nAnswer: {row['answer']}"
        documents.append(Document(page_content=text, metadata={"source": "company_policy"}))

print(f"Loaded {len(documents)} documents.")

# 2. Setup Embeddings
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Fallback for testing without key (Mock)
    print("WARNING: OPENAI_API_KEY not found. Using fake embeddings for testing setup.")
    from langchain_community.embeddings import FakeEmbeddings
    embeddings = FakeEmbeddings(size=1536)
else:
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# 3. Create Vector Store (ChromaDB)
persist_directory = "./chroma_db"
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(f"Ingestion complete. Vector DB saved to {persist_directory}")
