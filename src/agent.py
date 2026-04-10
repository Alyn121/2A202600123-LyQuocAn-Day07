from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        
        context_chunks = []
        for r in results:
            content = r.get("content", "")
            if content:
                context_chunks.append(content)
                
        context = "\n\n---\n\n".join(context_chunks)
        
        prompt = f"""You are a helpful assistant. Use the following context to answer the question. 
If the answer is not contained within the context, say "I don't know based on the provided context."

Context:
{context}

Question:
{question}

Answer:"""
        return self.llm_fn(prompt)

def get_gemini_llm(model_name: str = "gemini-2.5-flash") -> Callable[[str], str]:
    import os
    import google.generativeai as genai
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        
    model = genai.GenerativeModel(model_name)
    
    def llm_fn(prompt: str) -> str:
        response = model.generate_content(prompt)
        return response.text
        
    return llm_fn
