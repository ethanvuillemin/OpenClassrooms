import os
from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

# Chargement des variables d'environnement
load_dotenv()

# Configuration de ChatOpenAI
response_model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE"),
    max_tokens=8000,
    temperature=0,
)

# Définition de l'état partagé
class RAGState(TypedDict):
    question: str
    documents: List[Document]
    retrieved_docs: List[Document]
    answer: str
    error: str | None

# Configuration des embeddings
embeddings = HuggingFaceEmbeddings(
    model_name=os.getenv("EMBEDDING_MODEL")
)

# Template de prompt
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant qui répond aux questions en utilisant UNIQUEMENT les documents fournis. Si l'information n'est pas dans les documents, dis-le clairement."),
    ("user", """Documents:
{context}
Question: {question}
Réponds de manière concise et précise.""")
])

# Nœuds du graphe
def chunk_documents(state: RAGState) -> RAGState:
    """Découpe les documents en chunks"""
    print("Chunking des documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(state["documents"])
    state["documents"] = chunks
    print(f"{len(chunks)} chunks créés")
    return state

def create_vectorstore(state: RAGState) -> RAGState:
    """Crée la base vectorielle et indexe les documents"""
    print("Création de la base vectorielle...")
    vectorstore = FAISS.from_documents(state["documents"], embeddings)
    state["vectorstore"] = vectorstore
    print("Base vectorielle créée")
    return state

def retrieve_documents(state: RAGState) -> RAGState:
    """Recherche les documents pertinents"""
    print(f"Recherche pour: '{state['question']}'")
    vectorstore = state.get("vectorstore")
    if not vectorstore:
        state["error"] = "Base vectorielle non initialisée"
        return state
    docs = vectorstore.similarity_search(state["question"], k=3)
    state["retrieved_docs"] = docs
    print(f"{len(docs)} documents récupérés")
    return state

def generate_answer(state: RAGState) -> RAGState:
    """Génère la réponse avec le LLM"""
    print("Génération de la réponse...")
    if not state["retrieved_docs"]:
        state["answer"] = "Je n'ai pas trouvé d'informations pertinentes dans les documents."
        return state
    context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(state["retrieved_docs"])])
    chain = prompt_template | response_model
    response = chain.invoke({"context": context, "question": state["question"]})
    state["answer"] = response.content
    print("Réponse générée")
    return state

# Création du graphe
def create_simple_rag_graph():
    workflow = StateGraph(RAGState)
    workflow.add_node("chunk", chunk_documents)
    workflow.add_node("vectorize", create_vectorstore)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("generate", generate_answer)
    workflow.set_entry_point("chunk")
    workflow.add_edge("chunk", "vectorize")
    workflow.add_edge("vectorize", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()

# Test du workflow
# if __name__ == "__main__":
#     sample_docs = [
#         Document(page_content="Article 1101 du Code civil : Le contrat est un accord de volontés...", metadata={"source": "code_civil.txt"}),
#         Document(page_content="Article 1102 du Code civil : Le contrat est synallagmatique ou unilatéral...", metadata={"source": "code_civil.txt"}),
#     ]
#     app = create_simple_rag_graph()
#     initial_state = {"question": "Qu'est-ce qu'un contrat ?", "documents": sample_docs, "retrieved_docs": [], "answer": "", "error": None}
#     result = app.invoke(initial_state)
#     print(f"Question: {result['question']}\nRéponse: {result['answer']}")
