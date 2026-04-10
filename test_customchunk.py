import os
from src.chunking import CustomChunker

def run_custom_test():
    chunker = CustomChunker()
    files = ["khach_hang.txt", "nhahang.txt", "taxi.txt"]
    data_dir = "data"
    
    print("| File Name | Chunk Count | Avg Length | Strategy Type |")
    print("|-----------|-------------|------------|---------------|")
    
    for filename in files:
        path = os.path.join(data_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunker.chunk(text)
        avg_len = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
        print(f"| {filename:<10} | {len(chunks):<11} | {avg_len:<10.2f} | Custom (Headers) |")

if __name__ == "__main__":
    run_custom_test()
