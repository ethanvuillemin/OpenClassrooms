import json
import operator
import os
import re
import logging
import torch
from typing import Dict, List, Optional, Union, Annotated, Literal
from dotenv import load_dotenv
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dataclasses import dataclass
from tqdm import tqdm
from langchain_mistralai import ChatMistralAI

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class MessagesState:
    messages: Annotated[List[Union[HumanMessage, AIMessage, ToolMessage]], add_messages]
    recursion_count: int = 0  # Compteur de récursion

class LangGraphRAG:
    def __init__(
        self,
        pdf_path: str = "../data/code-civil",
        embedding_model_path: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        vectorstore_path: str = os.getenv("VECTORSTORE", "../vectorstore/faiss_index")
    ):
        self.pdf_path = pdf_path
        self.embedding_model_path = embedding_model_path
        self.vectorstore_path = vectorstore_path

        self.response_model = ChatMistralAI(
            model="mistral-small",
            temperature=0.1,
            max_tokens=4000,
            api_key=os.getenv("MISTRAL_API_KEY"),  # Correction : utiliser MISTRAL_API_KEY
        )
        self.grader_model = ChatMistralAI(
            model="mistral-tiny",
            temperature=0.1,
            max_tokens=4000,
            api_key=os.getenv("MISTRAL_API_KEY"),  # Correction : utiliser MISTRAL_API_KEY
        )
        self._setup_components()

    def _setup_components(self):
        """Setup all components for the RAG system"""
        # Détection GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        batch_size = 64 if device == "cuda" else 32

        logger.info(f"Using device: {device}")

        # Initialize embedding model optimisé
        self.huggingface_embedding_model = HuggingFaceBgeEmbeddings(
            model_name=self.embedding_model_path,
            model_kwargs={"device": device},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": batch_size
            }
        )

        # Charger ou créer le vectorstore
        if os.path.exists(self.vectorstore_path):
            logger.info("Loading existing vectorstore...")
            vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.huggingface_embedding_model,
                allow_dangerous_deserialization=True
            )
            logger.info("Vectorstore loaded successfully!")
        else:
            logger.info("Creating new vectorstore...")
            vectorstore = self._create_vectorstore()

            # Sauvegarder pour la prochaine fois
            os.makedirs(os.path.dirname(self.vectorstore_path), exist_ok=True)
            vectorstore.save_local(self.vectorstore_path)
            logger.info(f"Vectorstore saved to {self.vectorstore_path}")

        # Create retriever
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # Create retrieval tool
        self.retriever_tool = create_retriever_tool(
            retriever=self.retriever,
            name="retrieve_blog_posts",
            description="Search and return information about the french civil code.",
        )

        self.model_with_tools = self.response_model.bind_tools([self.retriever_tool])
        self._setup_graph()

    def _create_vectorstore(self):
        """Create vectorstore with optimized processing"""
        # Load documents
        logger.info("Loading PDF documents...")
        docs_before_split = self._load_pdf_from_directory(self.pdf_path)
        logger.info(f"Loaded {len(docs_before_split)} pages")

        # Splitter optimisé
        logger.info("Splitting documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        docs_after_split = text_splitter.split_documents(docs_before_split)
        logger.info(f"Created {len(docs_after_split)} chunks")

        # Vectorisation par batch avec barre de progression
        logger.info("Creating embeddings...")
        vectorstore = self._create_vectorstore_with_batches(docs_after_split)

        return vectorstore

    def _create_vectorstore_with_batches(self, docs):
        """Vectorisation optimisée par batch"""
        batch_size = 100

        # Première batch pour initialiser le vectorstore
        first_batch = docs[:batch_size]
        vectorstore = FAISS.from_documents(
            first_batch,
            self.huggingface_embedding_model
        )

        # Ajouter les autres batches
        for i in tqdm(range(batch_size, len(docs), batch_size), desc="Vectorizing"):
            batch = docs[i:i + batch_size]
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            vectorstore.add_texts(texts, metadatas=metadatas)

        return vectorstore

    def _load_pdf_from_directory(self, dir_path: str):
        """Load PDF files from directory with filtering"""
        documents = []

        if not os.path.exists(dir_path):
            logger.error(f"Directory not found: {dir_path}")
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        pdf_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.pdf')]

        if not pdf_files:
            logger.error(f"No PDF files found in {dir_path}")
            raise ValueError(f"No PDF files found in {dir_path}")

        for filename in tqdm(pdf_files, desc="Loading PDFs"):
            logger.info(f"Loading PDF: {filename}")
            loader = PyPDFLoader(os.path.join(dir_path, filename))
            docs = loader.load()

            # Filtrer les pages vides ou trop courtes
            docs = [doc for doc in docs if len(doc.page_content.strip()) > 50]

            # Ajouter les métadonnées (nom du fichier et numéro de page)
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["page"] = doc.metadata.get("page", "Unknown")

            documents.extend(docs)

        return documents

    def generate_query_or_response(self, state: MessagesState) -> Dict[str, List]:
        """Generate query or response based on the current state"""
        messages = state.messages
        recursion_count = state.recursion_count
        
        logger.info(f"Generating query or response... (Recursion count: {recursion_count})")
        
        # Si on a atteint 3 récursions, on force la génération de réponse
        if recursion_count >= 3:
            logger.info("Maximum recursion reached, generating answer without further retrieval...")
            question = ""
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    question = msg.content
                    break
            
            # Générer une réponse directe sans outils
            final_response = self.response_model.invoke(messages)
            return {
                "messages": [final_response],
                "recursion_count": recursion_count
            }
        
        response = self.model_with_tools.invoke(messages)
        return {
            "messages": [response],
            "recursion_count": recursion_count + 1  # Incrémenter le compteur
        }

    def grade_documents(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """Grade the relevance of retrieved documents"""
        messages = state.messages
        recursion_count = state.recursion_count

        if len(messages) < 2:
            logger.warning("Not enough messages to grade documents.")
            return "generate_answer"  # Passer directement à la génération

        try:
            # Trouver la question initiale
            question = ""
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    question = msg.content
                    break

            # Trouver le contenu de l'outil
            context = ""
            for msg in reversed(messages):
                if isinstance(msg, ToolMessage):
                    context = msg.content
                    break
                elif isinstance(msg, AIMessage) and msg.tool_calls:
                    # Si on a un message avec tool_calls mais pas encore de ToolMessage,
                    # on continue à chercher
                    continue

            if not question or not context:
                logger.warning("Empty question or context.")
                # Si on a atteint la limite de récursion, générer une réponse directe
                if recursion_count >= 3:
                    return "generate_answer"
                return "generate_answer"  # Passer directement à la génération

            logger.info("Grading documents for relevance...")
            prompt = f"""
            Évaluez si ce document est pertinent pour répondre à la question sur le code civil francais.

            Question: {question}
            Document: {context}

            Répondez uniquement par 'yes' si le document est pertinent, ou 'no' s'il ne l'est pas.
            """

            evaluation = self.grader_model.invoke([HumanMessage(content=prompt)])

            if "yes" in evaluation.content.lower():
                logger.info("Document graded as relevant.")
                return "generate_answer"
            else:
                logger.info("Document graded as not relevant.")
                # Si on a atteint la limite de récursion, générer une réponse directe
                if recursion_count >= 3:
                    return "generate_answer"
                return "generate_answer"  # Passer directement à la génération

        except Exception as e:
            logger.error(f"Error in grade_documents: {str(e)}")
            return "generate_answer"  # Passer directement à la génération

    def rewrite_question(self, state: MessagesState) -> Dict[str, List]:
        """Rewrite the question if documents are not relevant"""
        messages = state.messages
        last_message = messages[-1]
        recursion_count = state.recursion_count
        
        logger.info(f"Rewriting question for more specificity... (Recursion count: {recursion_count})")
        
        # Si on a atteint 3 récursions, on génère une réponse directe
        if recursion_count >= 3:
            logger.info("Maximum recursion reached, generating answer directly...")
            final_response = self.response_model.invoke(messages)
            return {
                "messages": [final_response],
                "recursion_count": recursion_count
            }
        
        new_message = HumanMessage(content=f"Please provide a more specific question about the civil code: {last_message.content}")
        return {
            "messages": [new_message],
            "recursion_count": recursion_count + 1  # Incrémenter le compteur
        }

    def generate_answer(self, state: MessagesState) -> Dict[str, List]:
        """Generate final answer based on retrieved documents"""
        messages = state.messages
        
        # Récupérer la question initiale
        question = ""
        for msg in messages:
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
        
        logger.info("Generating final answer with retrieved documents...")
        
        # Récupérer les documents à partir du retriever en utilisant la question
        docs = self.retriever.invoke(question)
        
        # Afficher les documents récupérés dans les logs
        logger.info(f"Top {len(docs)} retrieved documents:")
        sources = []
        for i, doc in enumerate(docs, 1):
            logger.info(f"Document {i}: {doc.page_content[:200]}...")
            logger.info(f"Source: {doc.metadata.get('source', 'Unknown')}")
            logger.info(f"Page: {doc.metadata.get('page', 'Unknown')}")
            
            source_info = {
                "document": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "content": doc.page_content[:200] + "..."
            }
            sources.append(source_info)
        
        # Créer le prompt final avec les documents
        if sources:
            # Remplacer les backslashes dans les chemins
            documents_text = ""
            for i, doc in enumerate(sources, 1):
                source = doc['document'].replace('\\', '/')
                documents_text += f"Document {i}: {doc['content']} (Source: {source}, page: {doc['page']})\n"
            
            final_prompt = (
                "Répondez à la question suivante en utilisant les informations des documents ci-dessous.\n"
                "À la fin de votre réponse, citez explicitement les sources utilisées sous la forme :\n"
                "'Sources : [Document X, page Y]'.\n\n"
                f"Question : Recherche dans le code civil:  {question}\n\n"
                f"Documents :\n{documents_text}"
            )
            
            final_response = self.response_model.invoke([HumanMessage(content=final_prompt)])
            return {
                "messages": [final_response],
                "recursion_count": state.recursion_count  # Conserver le compteur
            }
        else:
            # Si pas de documents récupérés, répondre avec le modèle sans contexte
            final_response = self.response_model.invoke(messages)
            return {
                "messages": [final_response],
                "recursion_count": state.recursion_count  # Conserver le compteur
            }

    def _should_use_tools(self, state: MessagesState) -> Literal["retrieve", "__end__"]:
        """Determine if tools should be used based on the last message"""
        messages = state.messages
        recursion_count = state.recursion_count
        
        if not messages:
            return "__end__"

        # Toujours utiliser les outils pour forcer le retrieval
        logger.info(f"Forcing retrieval for all questions... (Recursion count: {recursion_count})")
        return "retrieve"

    def _setup_graph(self):
        """Setup the LangGraph workflow"""
        workflow = StateGraph(MessagesState)

        # Add nodes
        workflow.add_node("generate_query_or_response", self.generate_query_or_response)
        workflow.add_node("retrieve", ToolNode([self.retriever_tool]))
        workflow.add_node("rewrite_question", self.rewrite_question)
        workflow.add_node("generate_answer", self.generate_answer)

        # Add edges
        workflow.add_edge(START, "generate_query_or_response")

        # Conditional edges
        workflow.add_conditional_edges(
            "generate_query_or_response",
            self._should_use_tools,
            {
                "retrieve": "retrieve",
                "__end__": END
            }
        )

        workflow.add_conditional_edges(
            "retrieve",
            self.grade_documents,
            {
                "generate_answer": "generate_answer",
                "rewrite_question": "rewrite_question"
            }
        )

        workflow.add_edge("generate_answer", END)
        workflow.add_edge("rewrite_question", "generate_query_or_response")

        # Compile the graph
        self.graph = workflow.compile()

    def invoke(self, question: str) -> str:
        """Invoke the RAG system with a question"""
        logger.info(f"Invoking RAG with question: {question}")
        initial_state = MessagesState(
            messages=[HumanMessage(content=question)],
            recursion_count=0  # Initialiser le compteur à 0
        )

        # Ajouter une configuration avec un limite de récursion plus haute pour permettre notre logique
        config = {"configurable": {"recursion_limit": 50}}
        
        result = self.graph.invoke(initial_state, config=config)

        # Correction : result est un dictionnaire, pas un objet
        if isinstance(result, dict) and "messages" in result and len(result["messages"]) > 0:
            return result["messages"][-1].content
        elif hasattr(result, 'messages') and len(result.messages) > 0:
            return result.messages[-1].content
        else:
            return "No response generated."

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation (rapide si vectorstore existe déjà)
    rag = LangGraphRAG(
        pdf_path="../data/code-civil",
        embedding_model_path=os.getenv("EMBEDDING_MODEL"),
        vectorstore_path="./vectorstore/faiss_index"
    )

    # Poser une question
    question = "Recherche quelles sont les conditions de validité d'un contrat selon le code civil? en une phrase courte stp"
    response = rag.invoke(question)
    logger.info(f"\nQuestion: {question}")
    logger.info(f"Réponse: {response}")