from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Load your extracted text
with open("document_text.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Step 1: Chunk the text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
)

chunks = text_splitter.create_documents([raw_text])

# Step 2: Create a vectorstore using OpenAI embeddings
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(openai_api_key="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"),

    persist_directory="vectorstore"
)

# Save the vectorstore for later chatbot use
vectorstore.persist()

print("✅ Vectorstore built and saved.")
