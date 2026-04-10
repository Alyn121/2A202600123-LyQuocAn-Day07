import os
import json
from src.chunking import ChunkingStrategyComparator

def test_new_data_strategies():
    comparator = ChunkingStrategyComparator()
    # Danh sách các file bạn muốn kiểm tra cho phần 3
    target_files = ["ĐIỀU KHOẢN CHUNG.txt", "khach_hang.txt"]
    data_dir = "data"
    
    print("### KẾT QUẢ PHẦN 3: BASELINE ANALYSIS ###\n")
    
    for filename in target_files:
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            print(f"Không tìm thấy file: {filename}")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        print(f"--- Đang xử lý tài liệu: {filename} ---")
        # Sử dụng chunk_size = 500
        results = comparator.compare(text, chunk_size=500)
        
        # In header bảng Markdown
        print("| Strategy | Chunk Count | Avg Length | Preserves Context? |")
        print("|----------|-------------|------------|-------------------|")
        
        for strategy, stats in results.items():
            # Đánh giá sơ bộ về Preserves Context
            context_quality = "High" if strategy == "by_sentences" else "Medium"
            if strategy == "fixed_size": context_quality = "Low"
            if strategy == "recursive": context_quality = "Very High"
                
            print(f"| {strategy:<15} | {stats['count']:<11} | {stats['avg_length']:<10.2f} | {context_quality:<18} |")
        print("\n")

if __name__ == "__main__":
    test_new_data_strategies()
