# rag_engine.py
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()
gemini_key = os.getenv("gemini_key")


# ---------------- LLM ----------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_key
)

# ---------------- LOAD EXCEL ----------------
excel_path = "FAQ_file.xlsx"  # must be in repo root

loader = UnstructuredExcelLoader(excel_path)
docs = loader.load()
texts = [d.page_content for d in docs]

# ---------------- VECTOR DB ----------------
vector_path = "faiss_index"

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if not os.path.exists(vector_path):
    db = FAISS.from_texts(texts, embedding_model)
    db.save_local(vector_path)
else:
    db = FAISS.load_local(vector_path, embedding_model, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 3})

# ---------------- PROMPT ----------------
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent FAQ assistant for Life & Half.
Use ONLY the context provided. Do not guess.

Context:
{context}

User Question:
{question}

Answer:
"""
)

chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)


def ask_bot(query):
    resp = chain({"query": query})
    answer = resp["result"]

    context = " ".join([d.page_content for d in resp["source_documents"]]).strip()

    if context == "" or len(context) < 10:
        return "I don't know. Please wait for the Human reply."

    bad_words = ["i don't know", "not sure", "cannot", "no information"]
    if any(b in answer.lower() for b in bad_words):
        return "I don't know. Please wait for the Human reply."

    return answer

