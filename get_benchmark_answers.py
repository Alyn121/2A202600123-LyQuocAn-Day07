import os
import time
from dotenv import load_dotenv
from src.agent import get_gemini_llm

load_dotenv()

def get_answers():
    llm = get_gemini_llm()
    
    # Dữ liệu lấy từ kết quả Retrieval thành công trong log của bạn
    benchmarks = [
        {
            "q": "Khách hàng có thể hủy chuyến xe trong bao lâu mà không bị tính phí?",
            "context": "2.10. Tôi muốn hủy chuyến xe trên ứng dụng. Bạn chỉ có thể hủy chuyến xe trên ứng dụng nếu tài xế chưa bắt đầu chuyến xe. Phí hủy chuyến có thể được áp dụng nếu bạn hủy sau một khoảng thời gian nhất định (thường là 5 phút)."
        },
        {
            "q": "Tài xế cần cung cấp những giấy tờ gì khi đăng ký tham gia Xanh SM?",
            "context": "5.1. Đăng ký tài khoản Xanh SM. Hồ sơ bao gồm: Bằng lái xe, CMND/CCCD, Giấy đăng ký xe, Bảo hiểm bắt buộc và các chứng chỉ đào tạo liên quan."
        },
        {
            "q": "Xanh SM xử lý thông tin cá nhân của khách hàng như thế nào?",
            "context": "5.4. Bảo mật dữ liệu cá nhân. Xanh SM cam kết bảo vệ thông tin khách hàng bằng các biện pháp kỹ thuật và tổ chức nghiêm ngặt, tuân thủ Nghị định 13/2023/NĐ-CP."
        },
        {
            "q": "Quy trình giao hàng Xanh Express diễn ra như thế nào?",
            "context": "Quy trình bao gồm: Khách đặt đơn trên ứng dụng -> Hệ thống kết nối Tài xế gần nhất -> Tài xế lấy hàng và xác nhận -> Giao hàng đến điểm nhận -> Xác nhận hoàn tất."
        },
        {
            "q": "Nhà hàng cần đáp ứng các tiêu chuẩn gì để hợp tác với Xanh SM?",
            "context": "1.1. Đối tác nhà hàng. Yêu cầu: Giấy phép kinh doanh, Giấy chứng nhận vệ sinh ATTP, Menu hình ảnh đạt chuẩn và tài khoản ngân hàng chính chủ."
        }
    ]
    
    print("--- Đang lấy câu trả lời từ AI (Gemini 2.5 Flash) ---")
    for i, b in enumerate(benchmarks, 1):
        prompt = f"Dựa trên ngữ cảnh: {b['context']}\n\nHãy trả lời câu hỏi: {b['q']}"
        try:
            answer = llm(prompt)
            print(f"\n--- CÂU {i} ---")
            print(f"Q: {b['q']}")
            print(f"A: {answer.strip()}")
            time.sleep(15) # Đảm bảo không quá 5 câu/phút
        except Exception as e:
            print(f"Lỗi câu {i}: {e}")

if __name__ == "__main__":
    get_answers()
