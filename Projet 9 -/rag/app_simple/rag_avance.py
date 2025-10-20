import os
from dotenv import load_dotenv
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.retrievers import BM25Retriever

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

# Définition de l'état avancé
class AdvancedRAGState(TypedDict):
    original_question: str
    rewritten_queries: List[str]
    query_type: str
    documents: List[Document]
    retrieved_docs_semantic: List[Document]
    retrieved_docs_lexical: List[Document]
    merged_docs: List[Document]
    reranked_docs: List[Document]
    answer: str
    confidence_score: float
    validation_result: dict
    cache_hit: bool
    error: str | None

# Configuration des embeddings
embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))

# Cache simple
query_cache = {}

# Nœuds du graphe avancé
def analyze_query(state: AdvancedRAGState) -> AdvancedRAGState:
    """Agent d'analyse de la requête"""
    print("Analyse de la requête...")
    query = state["original_question"]
    classifier_prompt = ChatPromptTemplate.from_messages([
        ("system", "Classifie la requête en: 'simple', 'multi_doc', ou 'comparative'"),
        ("user", "Question: {question}\nRéponds uniquement par: simple, multi_doc ou comparative")
    ])
    chain = classifier_prompt | response_model
    result = chain.invoke({"question": query})
    query_type = result.content.strip().lower()
    state["query_type"] = query_type if query_type in ["simple", "multi_doc", "comparative"] else "simple"
    print(f"Type détecté: {state['query_type']}")
    return state

def check_cache(state: AdvancedRAGState) -> AdvancedRAGState:
    """Vérifie si la réponse est en cache"""
    print("Vérification du cache...")
    query_key = state["original_question"].lower().strip()
    if query_key in query_cache:
        print("Cache HIT!")
        cached_result = query_cache[query_key]
        state["answer"] = cached_result["answer"]
        state["confidence_score"] = cached_result["confidence"]
        state["cache_hit"] = True
    else:
        print("Cache MISS")
        state["cache_hit"] = False
    return state

def should_use_cache(state: AdvancedRAGState) -> Literal["cached", "process"]:
    """Décision: utiliser le cache ou continuer le traitement"""
    return "cached" if state.get("cache_hit") else "process"

def rewrite_query(state: AdvancedRAGState) -> AdvancedRAGState:
    """Query rewriting: génère plusieurs variantes de la question"""
    print("Réécriture de la requête...")
    query = state["original_question"]
    rewriter_prompt = ChatPromptTemplate.from_messages([
        ("system", """Génère 2-3 variantes de la question qui utilisent:
- Des synonymes
- Des formulations différentes
- Des termes techniques si pertinent
Format: une variante par ligne, sans numérotation."""),
        ("user", "Question originale: {question}")
    ])
    chain = rewriter_prompt | response_model
    result = chain.invoke({"question": query})
    variants = [line.strip() for line in result.content.split("\n") if line.strip()]
    state["rewritten_queries"] = [query] + variants[:2]
    print(f"{len(state['rewritten_queries'])} variantes créées:")
    for i, q in enumerate(state["rewritten_queries"], 1):
        print(f"   {i}. {q}")
    return state

def semantic_search(state: AdvancedRAGState) -> AdvancedRAGState:
    """Recherche sémantique avec embeddings"""
    print("Recherche sémantique...")
    vectorstore = state.get("vectorstore")
    if not vectorstore:
        state["retrieved_docs_semantic"] = []
        return state
    all_docs = []
    seen_content = set()
    for query in state["rewritten_queries"]:
        docs = vectorstore.similarity_search_with_score(query, k=3)
        for doc, score in docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_content:
                doc.metadata["similarity_score"] = score
                all_docs.append(doc)
                seen_content.add(content_hash)
    state["retrieved_docs_semantic"] = all_docs[:5]
    print(f"{len(state['retrieved_docs_semantic'])} documents sémantiques")
    return state

def lexical_search(state: AdvancedRAGState) -> AdvancedRAGState:
    """Recherche lexicale BM25"""
    print("Recherche lexicale (BM25)...")
    documents = state.get("documents", [])
    if not documents:
        state["retrieved_docs_lexical"] = []
        return state
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 3
    docs = bm25_retriever.get_relevant_documents(state["original_question"])
    for doc in docs:
        doc.metadata["search_type"] = "lexical"
    state["retrieved_docs_lexical"] = docs
    print(f"{len(docs)} documents lexicaux")
    return state

def hybrid_merge(state: AdvancedRAGState) -> AdvancedRAGState:
    """Fusionne et déduplique les résultats sémantiques et lexicaux"""
    print("Fusion hybride des résultats...")
    semantic_docs = state.get("retrieved_docs_semantic", [])
    lexical_docs = state.get("retrieved_docs_lexical", [])
    merged = {}
    for doc in semantic_docs:
        content_hash = hash(doc.page_content)
        merged[content_hash] = {"doc": doc, "score": 0.7 * (1 - doc.metadata.get("similarity_score", 0))}
    for doc in lexical_docs:
        content_hash = hash(doc.page_content)
        if content_hash in merged:
            merged[content_hash]["score"] += 0.3
        else:
            merged[content_hash] = {"doc": doc, "score": 0.3}
    sorted_docs = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    state["merged_docs"] = [item["doc"] for item in sorted_docs[:5]]
    print(f"{len(state['merged_docs'])} documents fusionnés")
    return state

def rerank_documents(state: AdvancedRAGState) -> AdvancedRAGState:
    """Reranking avec un LLM pour affiner la pertinence"""
    print("Reranking des documents...")
    docs = state.get("merged_docs", [])
    if not docs:
        state["reranked_docs"] = []
        return state
    rerank_prompt = ChatPromptTemplate.from_messages([
        ("system", """Évalue la pertinence de chaque document pour répondre à la question.
Score de 0 à 10. Format: Document X: score"""),
        ("user", """Question: {question}
Documents:
{documents}""")
    ])
    docs_text = "\n\n".join([f"Document {i+1}:\n{doc.page_content[:300]}..." for i, doc in enumerate(docs)])
    chain = rerank_prompt | response_model
    result = chain.invoke({"question": state["original_question"], "documents": docs_text})
    scores = [7, 6, 5, 4, 3]
    try:
        lines = result.content.split("\n")
        scores = []
        for line in lines:
            if ":" in line and any(str(i) in line for i in range(11)):
                score_part = line.split(":")[-1].strip()
                score = float(''.join(c for c in score_part if c.isdigit() or c == '.'))
                scores.append(score)
    except Exception:
        pass
    docs_with_scores = list(zip(docs, scores[:len(docs)]))
    docs_with_scores.sort(key=lambda x: x[1], reverse=True)
    state["reranked_docs"] = [doc for doc, _ in docs_with_scores[:3]]
    print(f"Top {len(state['reranked_docs'])} documents après reranking")
    return state

def generate_answer_advanced(state: AdvancedRAGState) -> AdvancedRAGState:
    """Génération avancée avec métadonnées"""
    print("Génération de la réponse avancée...")
    docs = state.get("reranked_docs", [])
    if not docs:
        state["answer"] = "Je n'ai pas trouvé suffisamment d'informations pertinentes."
        state["confidence_score"] = 0.0
        return state
    context_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "inconnu")
        context_parts.append(f"[Source: {source}]\n{doc.page_content}")
    context = "\n\n---\n\n".join(context_parts)
    advanced_prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es un assistant expert qui répond avec précision en citant ses sources.
Instructions:
- Utilise UNIQUEMENT les informations des documents fournis
- Cite la source entre crochets [Source: X] après chaque affirmation
- Si plusieurs sources, compare et synthétise
- Si information manquante, dis-le clairement
- Sois concis mais complet"""),
        ("user", """Documents:\n{context}
Question: {question}
Réponds de manière structurée et cite tes sources.""")
    ])
    chain = advanced_prompt | response_model
    response = chain.invoke({"context": context, "question": state["original_question"]})
    state["answer"] = response.content
    state["confidence_score"] = min(len(docs) / 3.0, 1.0)
    print(f"Réponse générée (confiance: {state['confidence_score']:.2f})")
    return state

def validate_answer(state: AdvancedRAGState) -> AdvancedRAGState:
    """Valide la réponse pour détecter les hallucinations"""
    print("Validation de la réponse...")
    answer = state.get("answer", "")
    docs = state.get("reranked_docs", [])
    if not answer or not docs:
        state["validation_result"] = {"valid": False, "reason": "Données insuffisantes"}
        return state
    validation_prompt = ChatPromptTemplate.from_messages([
        ("system", """Vérifie si la réponse est fidèle aux documents sources.
Détecte:
- Hallucinations (infos non présentes)
- Contradictions
- Extrapolations excessives
Format JSON: {"valid": true/false, "issues": ["liste"], "confidence": 0-100}"""),
        ("user", """Documents sources:
{context}
Réponse à vérifier:
{answer}
Validation:""")
    ])
    context = "\n\n".join([doc.page_content for doc in docs])
    chain = validation_prompt | response_model
    result = chain.invoke({"context": context, "answer": answer})
    validation = {"valid": "true" in result.content.lower() or "valid" in result.content.lower(), "confidence": 85, "issues": []}
    state["validation_result"] = validation
    print(f"Validation: {'✓ Valide' if validation['valid'] else '✗ Problème détecté'}")
    return state

def save_to_cache(state: AdvancedRAGState) -> AdvancedRAGState:
    """Sauvegarde dans le cache si validation OK"""
    print("Sauvegarde en cache...")
    if state.get("validation_result", {}).get("valid", False):
        query_key = state["original_question"].lower().strip()
        query_cache[query_key] = {"answer": state["answer"], "confidence": state["confidence_score"]}
        print("Réponse mise en cache")
    else:
        print("Réponse non cachée (validation échouée)")
    return state

def route_by_complexity(state: AdvancedRAGState) -> Literal["simple_path", "complex_path"]:
    """Routing intelligent selon la complexité"""
    query_type = state.get("query_type", "simple")
    if query_type in ["multi_doc", "comparative"]:
        print("→ Route complexe")
        return "complex_path"
    else:
        print("→ Route simple")
        return "simple_path"

# Création du graphe avancé
def create_advanced_rag_graph():
    workflow = StateGraph(AdvancedRAGState)
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("cache_check", check_cache)
    workflow.add_node("cached_response", lambda s: s)
    workflow.add_node("rewrite", rewrite_query)
    workflow.add_node("semantic", semantic_search)
    workflow.add_node("lexical", lexical_search)
    workflow.add_node("merge", hybrid_merge)
    workflow.add_node("rerank", rerank_documents)
    workflow.add_node("generate", generate_answer_advanced)
    workflow.add_node("validate", validate_answer)
    workflow.add_node("cache_save", save_to_cache)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "cache_check")
    workflow.add_conditional_edges("cache_check", should_use_cache, {"cached": "cached_response", "process": "rewrite"})
    workflow.add_edge("cached_response", END)
    workflow.add_conditional_edges("rewrite", route_by_complexity, {"simple_path": "semantic", "complex_path": "semantic"})
    workflow.add_edge("semantic", "lexical")
    workflow.add_edge("lexical", "merge")
    workflow.add_edge("merge", "rerank")
    workflow.add_edge("rerank", "generate")
    workflow.add_edge("generate", "validate")
    workflow.add_edge("validate", "cache_save")
    workflow.add_edge("cache_save", END)
    return workflow.compile()

# Test du workflow avancé
# if __name__ == "__main__":
#     sample_docs = [
#         Document(page_content="Notre politique de remboursement: Délai de rétractation: 30 jours...", metadata={"source": "politique_remboursement.pdf"}),
#         Document(page_content="Garanties par forfait: Pack Basic: 1 an garantie...", metadata={"source": "garanties_forfaits.pdf"}),
#     ]
#     splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
#     chunks = splitter.split_documents(sample_docs)
#     vectorstore = FAISS.from_documents(chunks, embeddings)
#     app = create_advanced_rag_graph()
#     state = {
#         "original_question": "Quelle est la politique de remboursement ?",
#         "rewritten_queries": [],
#         "query_type": "",
#         "documents": chunks,
#         "retrieved_docs_semantic": [],
#         "retrieved_docs_lexical": [],
#         "merged_docs": [],
#         "reranked_docs": [],
#         "answer": "",
#         "confidence_score": 0.0,
#         "validation_result": {},
#         "cache_hit": False,
#         "error": None,
#         "vectorstore": vectorstore
#     }
#     result = app.invoke(state)
#     print(f"Question: {result['original_question']}\nRéponse: {result['answer']}")
