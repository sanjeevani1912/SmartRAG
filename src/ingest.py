import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def run_ingestion(data_dir, index_path):
    """
    Ingests documents from a directory, chunks them, embeds them, and saves to a FAISS index.
    """
    documents = []
    # Only load the 4 specific text files
    target_files = [
        "Document_1_Policy_Report.txt",
        "Document_2_News_Article.txt",
        "Document_3_Stakeholder_Memo.txt",
        "Document_4_Technical_Brief.txt"
    ]
    
    docs_path = os.path.join(data_dir, "Assignment_3_Docs")
    
    for filename in target_files:
        filepath = os.path.join(docs_path, filename)
        if os.path.exists(filepath):
            loader = TextLoader(filepath, encoding='utf-8')
            loaded_docs = loader.load()
            # Add source metadata explicitly
            for d in loaded_docs:
                d.metadata["source"] = filename
            documents.extend(loaded_docs)
        else:
            print(f"Warning: {filename} not found.")

    # Chunking Strategy:
    # Size: 1000 characters (approx 150-200 words)
    # Overlap: 200 characters (approx 30-40 words)
    # Justification: This size preserves the logic of regulatory clauses/paragraphs 
    # while the overlap ensures context continuity across splits.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents.")

    # Embedding model: sentence-transformers/all-MiniLM-L6-v2
    # Efficient, fast, and local.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create and save FAISS index
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(index_path)
    print(f"FAISS index saved to {index_path}")

if __name__ == "__main__":
    # Define paths
    BASE_DIR = os.getcwd()
    DATA_DIR = BASE_DIR # Assignment_3_Docs is inside SmartRAG root
    INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index")
    
    run_ingestion(DATA_DIR, INDEX_PATH)
