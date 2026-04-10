import os
from src.chunking import ChunkingStrategyComparator

def run_data_comparison():
    comparator = ChunkingStrategyComparator()
    data_dir = "data"
    
    # Chỉ lấy các file .txt hoặc .md
    files = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.md'))]
    
    print(f"{'File Name':<40} | {'Strategy':<15} | {'Count':<6} | {'Avg Len':<8}")
    print("-" * 75)
    
    for filename in files[:3]:  # Chạy thử 3 file đầu tiên
        file_path = os.path.join(data_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Chạy so sánh (chunk_size tùy chỉnh, ví dụ: 500)
        results = comparator.compare(text, chunk_size=500)
        
        for strategy, stats in results.items():
            print(f"{filename[:40]:<40} | {strategy:<15} | {stats['count']:<6} | {stats['avg_length']:<8.2f}")
        print("-" * 75)

if __name__ == "__main__":
    run_data_comparison()
