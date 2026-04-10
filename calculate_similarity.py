import os
from dotenv import load_dotenv
from src.embeddings import GeminiEmbedder
from src.chunking import compute_similarity

# Load API Key from .env
load_dotenv()

def run_similarity_test():
    # Initialize embedder
    embedder = GeminiEmbedder()
    
    # Define pairs of sentences for testing
    # You can customize these pairs based on your domain
    pairs = [
        ("tôi thích ăn thịt chó", "tôi rất yêu chó"),
        ("Tôi yêu thích động vật.", "tôi ghét chó"),
        ("nhà vua ", "Con mèo"),
        ("Làm sao để đặt xe trên ứng dụng?", "Hướng dẫn các bước đặt chuyến xe qua app."),
        ("Giá cước chuyến xe là bao nhiêu?", "Tôi muốn hủy tài khoản cá nhân.")
    ]
    
    print("### KẾT QUẢ PHẦN 5: SIMILARITY PREDICTIONS ###\n")
    print("| Pair | Sentence A | Sentence B | Actual Score | Prediction Correct? |")
    print("|------|-----------|-----------|--------------|---------------------|")
    
    for i, (sent_a, sent_b) in enumerate(pairs, 1):
        # Get embeddings using __call__
        vec_a = embedder(sent_a)
        vec_b = embedder(sent_b)
        
        # Compute similarity
        score = compute_similarity(vec_a, vec_b)
        
        # Prediction logic (based on semantic relation)
        # Note: You should fill the 'Dự đoán' in report before looking at this
        print(f"| {i} | {sent_a} | {sent_b} | {score:<12.4f} | [Tự điền] |")

if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        print("Error: GEMINI_API_KEY is not set correctly in .env file.")
    else:
        run_similarity_test()
