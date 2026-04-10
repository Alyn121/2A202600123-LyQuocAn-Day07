import os
from dotenv import load_dotenv
from src.embeddings import GeminiEmbedder
from src.chunking import CustomChunker
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent, get_gemini_llm
from src.models import Document

# Load environment variables
load_dotenv()

def run_section_6_benchmark():
    # 1. Setup Components
    # Using gemini-embedding-001 as verified earlier
    embedder = GeminiEmbedder()
    chunker = CustomChunker()
    # Ensure a fresh collection for the benchmark
    store = EmbeddingStore(collection_name="benchmark_collection", embedding_fn=embedder)
    
    # Initialize LLM and Agent
    llm = get_gemini_llm()
    agent = KnowledgeBaseAgent(store, llm_fn=llm)
    
    # 2. Load and Index Documents
    data_files = ["khach_hang.txt", "nhahang.txt", "taxi.txt"]
    data_dir = "data"
    
    print("--- [1/3] Đang nạp dữ liệu vào Vector Store... ---")
    import time
    for filename in data_files:
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = chunker.chunk(text)
            docs = [Document(id=f"{filename}_{i}", content=c, metadata={"source": filename}) for i, c in enumerate(chunks)]
            store.add_documents(docs)
            print(f"   + Đã nạp {len(docs)} chunks từ {filename}")
            time.sleep(5) # Safety delay between large files
    
    # 3. Define Benchmark Queries from REPORT.md
    queries = [
        "Khách hàng có thể hủy chuyến xe trong bao lâu mà không bị tính phí?",
        "Tài xế cần cung cấp những giấy tờ gì khi đăng ký tham gia Xanh SM?",
        "Xanh SM xử lý thông tin cá nhân của khách hàng như thế nào?",
        "Quy trình giao hàng Xanh Express diễn ra như thế nào?",
        "Nhà hàng cần đáp ứng các tiêu chuẩn gì để hợp tác với Xanh SM?"
    ]
    
    # 4. Run Benchmark
    print("\n--- [2/3] Đang chạy truy vấn RAG... ---")
    print("\n| # | Query | Top-1 Retrieved Chunk (Tóm tắt) | Score | Agent Answer (Tóm tắt) |")
    print("|---|-------|--------------------------------|-------|------------------------|")
    
    for i, query in enumerate(queries, 1):
        # SEARCH first to get top-1 chunk & score
        search_results = store.search(query, top_k=1)
        top_chunk = "N/A"
        score = 0.0
        if search_results:
            top_chunk = search_results[0]['content'][:100].replace("\n", " ").replace("|", " ") + "..."
            score = search_results[0].get('score', 0.0)
        
        # ANSWER from Agent
        try:
            answer = agent.answer(query)
            answer_summary = answer[:150].replace("\n", " ").replace("|", " ") + "..."
        except Exception as e:
            answer_summary = f"Error: {str(e)}"
        
        print(f"| {i} | {query} | {top_chunk} | {score:.4f} | {answer_summary} |")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Lỗi: Vui lòng cấu hình GEMINI_API_KEY trong file .env")
    else:
        run_section_6_benchmark()
