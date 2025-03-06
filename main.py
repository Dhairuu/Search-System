import os
import chromadb
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer
from tavily import TavilyClient
from typing import TypedDict, List
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv()


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


DATA_EXPIRY_DAYS = 7
SCORE_THRESHOLD = 0.56
DISTANCE_THRESHOLD = 0.45


class ResearchState(TypedDict):
    query: str
    documents: List[str]
    metadatas: List[dict]
    answer: str

tavily = TavilyClient(api_key=TAVILY_API_KEY)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_DB")
collection = chroma_client.get_or_create_collection(name="search_results", metadata={"hnsw:space": "cosine"})

def is_result_outdated(metadata):
    if not metadata or "timestamp" not in metadata:
        return True
    try:
        result_date = datetime.strptime(metadata["timestamp"], "%Y-%m-%d")
    except ValueError:
        return True
    return result_date < datetime.now() - timedelta(days=DATA_EXPIRY_DAYS)

def fetch_and_store(query: str):
    """Fetches search results and stores them in the database."""
    search_result = tavily.search(query, max_result=5, include_raw_content=True, include_images=True)
    documents, metadatas, ids, embeddings = [], [], [], []
    
    for result in search_result.get("results", []):
        score = result.get("score", 0)
        if score < SCORE_THRESHOLD:
            continue
        
        content = result.get("raw_content") or result.get("content", "")
        embedded_content = embedding_model.encode(content)
        
        metadata = {
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "score": score,
            "timestamp": datetime.now().strftime("%Y-%m-%d")
        }
        
        documents.append(content)
        metadatas.append(metadata)
        ids.append(str(uuid.uuid4()))
        embeddings.append(embedded_content.tolist())
    
    if documents:
        collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    
    return {"documents": documents, "metadatas": metadatas}

def get_relevant_results(state: ResearchState):
    """Retrieves relevant documents from the database or fetches new ones."""
    query_embedding = embedding_model.encode(state["query"]).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    # print(f"The result is: {results}")
    if results["documents"]:
        filtered_pairs = [
            (doc, meta) for doc_list, dist_list, meta_list in zip(results["documents"], results["distances"], results["metadatas"])
            for doc, dist, meta in zip(doc_list, dist_list, meta_list) if dist < DISTANCE_THRESHOLD
        ]
        # print(f"The filtered result is: {filtered_pairs}")
        if filtered_pairs:
            print("😊 Getting the information from the database")
            return {"documents": [doc for doc, _ in filtered_pairs], "metadatas": [meta for _, meta in filtered_pairs]}
    
    return fetch_and_store(state["query"])

def draft_answer(state: ResearchState):
    """Generates an AI-based answer using retrieved documents."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=GEMINI_API_KEY)
    
    documents, metadatas = state["documents"], state["metadatas"]
    if not documents:
        return {"answer": "Sorry, I don't have enough information to answer this question."}
    
    formatted_context = "\n\n".join([
        f"Source: {meta.get('title', 'Unknown')} ({meta.get('url', 'No URL')})\nSummary: {doc[:500]}..."
        for doc, meta in zip(documents, metadatas)
    ])
    
    system_message = "You are an AI that provides structured answers based on given context. Cite sources."
    human_message = f"User Question: {state['query']}\n\nSources:\n{formatted_context}\n\nGenerate a well-structured response."
    return {"answer": llm.invoke(system_message + "\n\n" + human_message)}

graph = StateGraph(ResearchState)

graph.add_node("research_agent", get_relevant_results)
graph.add_node("answer_agent", draft_answer)

graph.set_entry_point("research_agent")
graph.add_edge("research_agent", "answer_agent")
graph.add_edge("answer_agent", "__end__")


executor = graph.compile()

def run_research_system(query):
    response = executor.invoke({"query": query})
    return response["answer"]

if __name__ == "__main__":
    while True:
        user_query = input("\nEnter your question (or type 'exit' to quit): ")
        if user_query.lower() == "exit":
            print("Goodbye! 👋")
            break
        
        print("\n🔍 Running Research System...")
        answer = run_research_system(user_query)
        print("\n💡 Answer:")
        print(answer.content)