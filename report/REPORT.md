# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Lý Quốc AN]
**Nhóm:** [D3-C401]
**Ngày:** [10/4/2026]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *high cosine similarity nghĩa là hai vector có cùng hướng, tức là hai câu có cùng ý nghĩa, ví dụ nếu cosine similarity bằng 1 thì hai câu hoàn toàn giống nhau, nếu bằng 0 thì hai câu hoàn toàn khác nhau, nếu bằng -1 thì hai câu hoàn toàn khác nhau*
**Ví dụ HIGH similarity:**
- Sentence A:chó là bạn 
- Sentence B:tôi yêu chó 
- Tại sao tương đồng:

**Ví dụ LOW similarity:**
- Sentence A:chó là bạn 
- Sentence B:hôm nay trời đẹp
- Tại sao khác:

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Vì text embeding có đọ dài khác nhau nên khi tính khoảng cách Euclidean sẽ bị ảnh hưởng bởi độ dài, còn cosine similarity thì không bị ảnh hưởng bởi độ dài*

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:
> (10000 - 50) / (500 - 50) + 1 = 23 chunks*
> *Đáp án: 23 chunks*

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu: overlap tăng lên thì chunk count giảm đi, vì overlap nhiều hơn thì mỗi chunk sẽ có nhiều nội dung hơn*

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Xanh SM

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* Bởi vì chưa thấy sự tối ưu của chatbot trong việc trả lời các câu hỏi của tài xế về các quy định, chính sách của Xanh SM, nên nhóm muốn tìm hiểu và cải thiện nó.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Chính sách bảo vệ dữ liệu cá nhân.txt | https://www.xanhsm.com/helps | 36,439 | category= chính sách, source=xanhsm.com |
| 2 | donhang.txt|https://www.xanhsm.com/news/so-tay-van-hanh-dich-vu-giao-hang-xanh-express |15,104 |category=quy trình , source=xanhsm.com |
| 3 | ĐIỀU KHOẢN CHUNG.txt|https://www.xanhsm.com/helps |208,756 |category= Điều khoản,dịch vụ, source=xanhsm.com|
| 4 |khach_hang.txt|https://www.xanhsm.com/terms-policies/general?terms=12 |52,702 |category = hỏi đáp hỗ trợ khách hàng, audience = khách hàng  |
| 5 |nhahang.txt|https://www.xanhsm.com/terms-policies/general?terms=10 |38,996 | category=chính sách nhà hàng, source=xanhsm.com |
|6  |tai_xe.txt | https://www.xanhsm.com/terms-policies/general?terms=6|11,424|category=điều khoản của tài xế, audience = tài xế|
### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|| category | string | `chính sách ` , `quy trình `,`Điều khoản ` | Lọc theo loại tài liệu, tránh trả về chunk không liên quan loại nội dung |
| source | string | `xanhsm.com` | Truy vết nguồn gốc tài liệu, hỗ trợ citation và kiểm tra độ tin cậy |
| audience | string | `tài xế`, `khách hàng ` | Lọc theo đối tượng người dùng, trả về nội dung phù hợp với từng nhóm |

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu **khach_hang.txt**:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| khach_hang.txt | FixedSizeChunker (`fixed_size`) | 88 | 499.17 | Low (cắt ngang ý) |
| khach_hang.txt | SentenceChunker (`by_sentences`) | 113 | 347.65 | Medium (theo câu) |
| khach_hang.txt | RecursiveChunker (`recursive`) | 98 | 401.90 | High (theo đoạn văn) |

### Strategy Của Tôi

**Loại:** CustomChunker (Header-based)

**Mô tả cách hoạt động:**
> Strategy này sử dụng Regex để nhận diện các tiêu đề được đánh số (pattern: `1. `, `1.1. `, `2.1.3. `) nằm ở đầu dòng. Văn bản được tách thành các đoạn lớn bắt đầu từ tiêu đề này cho đến khi gặp tiêu đề tiếp theo. Cách này giúp gom toàn bộ nội dung của một mục hướng dẫn/FAQ vào cùng một khối thông tin duy nhất.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Domain hỗ trợ khách hàng (FAQ/SOP) thường trình bày theo từng vấn đề riêng biệt. Việc cắt theo đầu mục (section) đảm bảo AI luôn nhận được toàn bộ quy trình giải quyết vấn đề đó thay vì chỉ nhận được một vài mảnh vụn nếu dùng các phương pháp cắt theo số lượng từ hay câu.

**Code snippet (nếu custom):**
```python
class CustomChunker:
    def chunk(self, text: str) -> list[str]:
        header_pattern = re.compile(r'^(\d+(\.\d+)*\.\s?.*)', re.MULTILINE)
        matches = list(header_pattern.finditer(text))
        # ... logic tách text dựa vào start/end của matches ...
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| khach_hang.txt | RecursiveChunker | 98 | 401.90 | High |
| khach_hang.txt | **Custom (Header)** | 56 | 704.55 | **Very High** (Đúng mục tiêu) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| **Tôi** | **CustomChunker** | **10** | **Gom trọn vẹn ngữ cảnh của mỗi đầu mục FAQ, không bị cắt vụn thông tin.** | **Chunk có thể rất dài nếu một đầu mục chứa quá nhiều nội dung.** |
| Khánh | SentenceChunker | 8 | Giữ câu hoàn chỉnh, ngữ nghĩa đầy đủ, ít chunk hơn | Chunk dài hơn, tốn nhiều token hơn khi embed |
| Thư | RecursiveChunker | 6 | Linh hoạt với nhiều loại văn bản, chunk nhỏ hơn | Chunk quá ngắn (~130–139 ký tự), dễ mất ngữ cảnh |
| Lực | FixedSizeChunker | 5 | Đơn giản, dễ kiểm soát kích thước | Cắt giữa câu, chunk mất nghĩa, retrieval kém chính xác |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Strategy tốt nhất cho domain này là CustomChunker vì nó có thể tách text thành các đoạn lớn bắt đầu từ tiêu đề này cho đến khi gặp tiêu đề tiếp theo. Cách này giúp gom toàn bộ nội dung của một mục hướng dẫn/FAQ vào cùng một khối thông tin duy nhất.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng Regex `r'(?<=\.) |(?<=\!) |(?<=\?) |(?<=\.)\n'` để tách câu. Sau đó nhóm các câu lại theo số lượng `max_sentences_per_chunk`. Cách này tốt hơn FixedSize nhưng vẫn có thể cắt đôi một đoạn văn nếu đoạn văn đó có quá nhiều câu.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán đệ quy thử split bằng `\n\n`, rồi đến `\n`, `. `, ` ` cho đến khi đoạn text nhỏ hơn `chunk_size`. Đây là baseline mạnh vì nó ưu tiên giữ các đoạn văn đi cùng nhau.

**`CustomChunker.chunk`** — approach:
> Dùng `re.MULTILINE` và pattern `^(\d+(\.\d+)*\.\s?.*)` để "bắt" chính xác các đầu mục đánh số của tài liệu FAQ. Toàn bộ nội dung dưới mỗi đầu mục được giữ nguyên để bảo đảm tính toàn vẹn của thông tin cứu hộ/hướng dẫn.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Lưu trữ vector vào `chromadb.EphemeralClient`. Trong `add_documents`, tôi thêm một suffix số thứ tự vào ID của mỗi chunk để cho phép lưu nhiều phần của cùng một Document ID mà không bị trùng khóa chính. Hàm `search` chuyển đổi khoảng cách sang similarity score bằng công thức `1.0 - distance`.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` dùng tham số `where` của ChromaDB để filter metadata (ví dụ: `department`) trước khi tìm kiếm vector. `delete_document` thực hiện xóa tất cả các bản ghi có metadata `doc_id` tương ứng bằng lệnh `collection.delete()`.

### KnowledgeBaseAgent

**`answer`** — approach:
> Prompt được thiết kế gồm 3 phần: (1) Chỉ dẫn vai trò chuyên gia, (2) Bối cảnh (Context) được trích xuất từ database, và (3) Câu hỏi của khách hàng. Một ràng buộc quan trọng là Agent không được bịa thông tin nếu Context không có, giúp giảm thiểu hiện tượng AI ảo tưởng.

### Test Results

platform win32 -- Python 3.9.25, pytest-8.4.2, pluggy-1.6.0 -- D:\coding\conda\envs\dl_env\python.exe
cachedir: .pytest_cache
rootdir: D:\Work\aithucchien\Day-07-Lab-Data-Foundations
plugins: anyio-4.12.1, dash-4.0.0, langsmith-0.4.37
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                            [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                     [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                              [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                               [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                    [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                    [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                          [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                           [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                         [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                           [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                           [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                      [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                  [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                            [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                   [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                       [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                 [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                       [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                           [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                             [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                               [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                     [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                          [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                            [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                             [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                      [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                     [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                            [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                       [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                           [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                 [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                           [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED        [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                      [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                     [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED         [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                    [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED             [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED   [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED       [100%]

================================================== warnings summary ===================================================
..\..\..\coding\conda\envs\dl_env\lib\site-packages\google\api_core\_python_version_support.py:234
  D:\coding\conda\envs\dl_env\lib\site-packages\google\api_core\_python_version_support.py:234: FutureWarning: You are using a non-supported Python version (3.9.25). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
    warnings.warn(message, FutureWarning)

..\..\..\coding\conda\envs\dl_env\lib\site-packages\google\auth\__init__.py:54
  D:\coding\conda\envs\dl_env\lib\site-packages\google\auth\__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
    warnings.warn(eol_message.format("3.9"), FutureWarning)

..\..\..\coding\conda\envs\dl_env\lib\site-packages\google\oauth2\__init__.py:40
  D:\coding\conda\envs\dl_env\lib\site-packages\google\oauth2\__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
    warnings.warn(eol_message.format("3.9"), FutureWarning)

src\embeddings.py:67
  D:\Work\aithucchien\Day-07-Lab-Data-Foundations\src\embeddings.py:67: FutureWarning:

  All support for the `google.generativeai` package has ended. It will no longer be receiving
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:

  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

    import google.generativeai as genai

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================================== 42 passed, 4 warnings in 3.36s ============================================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Actual Score | Prediction Correct? |
|------|-----------|-----------|--------------|---------------------|
| 1 | tôi thích ăn thịt chó | tôi rất yêu chó | 0.8999       | sai |
| 2 | Tôi yêu thích động vật. | tôi ghét chó | 0.8282       | sai |
| 3 | nhà vua  | Con mèo | 0.8090       | sai |
| 4 | Làm sao để đặt xe trên ứng dụng? | Hướng dẫn các bước đặt chuyến xe qua app. | 0.9583       | đúng |
| 5 | Giá cước chuyến xe là bao nhiêu? | Tôi muốn hủy tài khoản cá nhân. | 0.7516       | sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> **Kết quả bất ngờ nhất là pair 1, 2, 3 đều sai, trong khi pair 4 và 5 đúng. Điều này cho thấy embeddings biểu diễn nghĩa không hoàn toàn chính xác, chỉ dựa vào một vài keywword để đoán, và cần phải có thêm các phương pháp để cải thiện độ chính xác.**

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Khách hàng có thể hủy chuyến xe trong bao lâu mà không bị tính phí? | Khách hàng có thể hủy chuyến miễn phí trong vòng 5 phút sau khi đặt xe. |
| 2 | Tài xế cần cung cấp những giấy tờ gì khi đăng ký tham gia Xanh SM? | Tài xế cần cung cấp bằng lái xe, CMND/CCCD, đăng ký xe và bảo hiểm còn hiệu lực. |
| 3 | Xanh SM xử lý thông tin cá nhân của khách hàng như thế nào? | Xanh SM bảo vệ dữ liệu cá nhân theo quy định pháp luật, không chia sẻ cho bên thứ ba nếu không có sự đồng ý. |
| 4 | Quy trình giao hàng Xanh Express diễn ra như thế nào? | Khách đặt đơn → tài xế nhận đơn → lấy hàng → giao hàng → xác nhận hoàn thành. |
| 5 | Nhà hàng cần đáp ứng các tiêu chuẩn gì để hợp tác với Xanh SM? | Nhà hàng cần đảm bảo vệ sinh thực phẩm, giấy phép kinh doanh hợp lệ và tuân thủ chính sách đối tác. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (Tóm tắt) | Score | Agent Answer (Tóm tắt) |
|---|-------|--------------------------------|-------|------------------------|
| 1 | Khách hàng có thể hủy chuyến xe trong bao lâu? | 2.10. Bạn chỉ có thể hủy nếu tài xế chưa bắt đầu. Thường miễn phí trong 5 phút. | 0.6919 | Khách hàng có thể hủy chuyến xe miễn phí trong vòng 5 phút đầu tiên sau khi đặt. |
| 2 | Tài xế cần giấy tờ gì để đăng ký Xanh SM? | 5.1. Hồ sơ: Bằng lái xe, CMND/CCCD, Đăng ký xe, Bảo hiểm bắt buộc... | 0.6985 | Cần: Bằng lái xe, CMND/CCCD, Giấy đăng ký xe, Bảo hiểm bắt buộc và chứng chỉ liên quan. |
| 3 | Xanh SM xử lý thông tin cá nhân như thế nào? | 5.4. Cam kết bảo mật tuân thủ Nghị định 13/2023/NĐ-CP và các quy định pháp luật. | 0.7347 | Thông tin được bảo mật nghiêm ngặt theo Nghị định 13/2023/NĐ-CP, không chia sẻ trái phép. |
| 4 | Quy trình giao hàng Xanh Express? | Khách đặt đơn -> Tài xế nhận -> Lấy hàng -> Giao hàng -> Xác nhận hoàn tất. | 0.6559 | Quy trình: Đặt đơn, Kết nối tài xế, Lấy hàng, Giao hàng và Xác nhận hoàn thành qua ứng dụng. |
| 5 | Tiêu chuẩn để nhà hàng hợp tác là gì? | 1.1. Yêu cầu: GPKD, Chứng nhận ATTP, Menu đạt chuẩn và Tài khoản ngân hàng. | 0.8252 | Nhà hàng cần GPKD, Chứng nhận vệ sinh ATTP, thực đơn đúng chuẩn và tài khoản chính chủ. |

### Đánh giá của tôi về hệ thống RAG

**Hệ thống tìm kiếm (Retrieval) có tìm đúng chunk chứa câu trả lời không?**
> Hệ thống tìm kiếm hoạt động rất hiệu quả với `CustomChunker`. Tỷ lệ tìm đúng chunk (Top-1) đạt gần 100% nhờ việc giữ nguyên các đầu mục lớn theo cấu trúc của tài liệu gốc.

**Agent có bị hallucinate (bịa thông tin) không?**
> Agent không bị hallucinate. Nhờ vào prompt constraint ("If the answer is not contained within the context..."), Agent chỉ trả lời dựa trên thông tin có trong chunk được trích xuất.

**Theo bạn, cần cải thiện gì để RAG tốt hơn?**
> Cần cải thiện tốc độ phản hồi bằng cách nâng cấp quota API (tránh lỗi 429) và có thể kết hợp thêm Reranking để đảm bảo chunk tốt nhất luôn đứng vị trí số 1 khi dữ liệu trở nên khổng lồ.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *học được các cách chunking khác nhau *

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *học được các cách chia querry*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *sẽ chia nhỏ từng chung trong các chunk lớn, không để chunk quá ít mà lại quá lớn như hiện tại*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân |  5 |
| Document selection | Nhóm | 10 |
| Chunking strategy | Nhóm | 14 |
| My approach | Cá nhân | 10 |
| Similarity predictions | Cá nhân | 5 |
| Results | Cá nhân | 10 |
| Core implementation (tests) | Cá nhân | 29 |
| Demo | Nhóm | 4 |
| **Tổng** | | **86/90** |
