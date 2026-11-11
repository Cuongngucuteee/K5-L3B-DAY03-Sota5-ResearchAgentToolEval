# Báo cáo cá nhân — Hoàng Thế Phong - 2A202603832

## 1. Thông tin thành viên

- Họ tên: Hoàng Thế Phong
- MSSV: `2A202603832`
- Email: `phonghoangthe112@gmail.com`
- Vai trò trong nhóm: **Thành viên A — Tối ưu System Prompt, Tool Declarations & Quản lý Versioning (`v0`–`v3`)**

## 2. Phần việc phụ trách

- Thiết lập kết nối provider với model **Gemini 3.5 Flash** (`provider=gemini`) và chạy kiểm tra `preflight_provider.py`, đảm bảo `pytest` contract test xanh trước khi đo.
- Chạy đánh giá baseline `v0` trên bộ 20 test case chuẩn (`starter_v0/data/eval_base.json`) và phân loại lỗi (`wrong_tool`, `wrong_arg_value`, `missing_info`, `wrong_boundary`) từ file log thực tế.
- Thực hiện tối ưu theo vòng lặp dựa trên bằng chứng (evidence-driven) qua 3 phiên bản `v1`, `v2`, `v3` — mỗi phiên bản kiểm chứng đúng **một** giả thuyết độc lập trên `starter_v0/artifacts/system_prompt.md` hoặc `starter_v0/artifacts/tools.yaml`.
- Phối hợp với thành viên C để tích hợp mô tả và quy ước tham số của tool mới `hn_search` vào `starter_v0/artifacts/tools.yaml`.
- Ghi nhận đầy đủ lịch sử thực nghiệm vào `starter_v0/artifacts/version_log.csv` và tổng hợp bảng phân tích B1, B2 vào `report/team/notes/A_versions.md` để nhóm trưởng ghép vào báo cáo nhóm.

## 3. Đóng góp cụ thể

### 3.1. Chạy Baseline `v0` và Phân tích lỗi (Failure Analysis)
- Chạy đánh giá `v0` với prompt và tool declarations gốc của starter: đạt **13/20 case (`case_accuracy = 0.65`, `routing_accuracy = 0.80`, `argument_accuracy = 0.65`, `multiturn_accuracy = 0.6667`, `provider_error_cases = 0`)**.
- Phân tích log JSON của 7 case FAIL ở `v0` và xác định 2 nhóm nguyên nhân gốc rễ:
  1. **Nhóm lỗi do 3 chỉ dẫn xấu cố ý trong `system_prompt.md` (4 case):**
     - `R10_missing_handle` (`missing_info`): Model tự đoán `screenname="sama"` và gọi `timeline` thay vì hỏi lại bằng `clarify`.
     - `R11_missing_url` (`missing_info`): Model tự gọi `lookup` đoán bài viết thay vì gọi `clarify` yêu cầu người dùng cung cấp URL.
     - `R12_confirm_before_send` (`wrong_boundary`): Model gọi thẳng `send(confirmed=true)` mà không hỏi xác nhận người dùng trước.
     - `R13_parallel_web_and_tweets` (`wrong_tool`): Do prompt ép hoàn thành trong 1 bước với 1 tool, model chỉ gọi `lookup` mà bỏ sót `social_search`.
  2. **Nhóm lỗi do thiếu quy ước tham số trong `tools.yaml` (3 case):**
     - `R03_web_news_routing`, `M02_carryover_timeframe`, `M06_switch_tool`: Model chọn đúng tool `lookup` nhưng truyền `query` dư các từ chỉ thời gian/loại tin (`"AI news today"`, `"robotics news today"`, `"OpenAI news"`) thay vì từ khóa chủ đề ngắn gọn (`"AI"`, `"robotics"`, `"OpenAI"`).

### 3.2. Ba vòng lặp tối ưu (`v1` → `v2` → `v3`)

| Version | File thay đổi | Giả thuyết kiểm chứng (1 giả thuyết / version) | `case_acc` | `routing_acc` | `arg_acc` | `multiturn_acc` |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`v0`** | *(Baseline)* | Đo hành vi gốc trước khi sửa. | 0.65 | 0.80 | 0.65 | 0.6667 |
| **`v1`** | `system_prompt.md` | Bỏ 3 chỉ dẫn xấu (đoán mò, gửi không xin phép, ép 1 tool) và thêm quy tắc gọi `clarify` khi thiếu thông tin / trước khi `send`, cho phép gọi nhiều tool sẽ khắc phục các lỗi `missing_info`, `wrong_boundary`, `wrong_tool`. | 0.45 | 0.65 | 0.45 | 0.1667 |
| **`v2`** | `system_prompt.md` | Quy tắc "không bao giờ đoán handle" ở `v1` quá rộng khiến model bị *over-clarify* (hỏi lại cả handle của người nổi tiếng như Sam Altman, Elon Musk ở `R01`, `R05`, `M01`, `M03`, `M05`). Tinh chỉnh lại ranh giới: chỉ `clarify` khi thực sự khuyết tên người/tài khoản hoặc URL; nếu đã nêu tên nhân vật/tổ chức nổi tiếng thì ánh xạ trực tiếp sang handle chuẩn không có `@`. | 0.75 | 1.00 | 0.75 | 0.6667 |
| **`v3`** | `tools.yaml` | Viết lại `description` toàn bộ tool (nêu rõ khi nào dùng / không dùng) và bổ sung quy ước tham số (`query` chỉ lấy từ khóa gốc không kèm `"news/today"`, handle không có `@`, `topic=news`, `timeframe`, `search_type=Top|Latest`, `send` cần `confirmed=true`) sẽ khắc phục lỗi `wrong_arg_value`. | **0.85** | **1.00** | **0.85** | **1.00** |

### 3.3. Đồng bộ mô tả tool mới (`hn_search`)
- Cập nhật mô tả chi tiết cho tool `hn_search` (tìm bài viết, câu hỏi và thảo luận trên Hacker News qua Algolia API, hỗ trợ sắp xếp theo `relevance` hoặc `date`, trả về error dict an toàn khi lỗi mạng) vào `starter_v0/artifacts/tools.yaml` và kiểm tra lại với `pytest tests/test_tool_contract.py` (60/60 test passed).

## 4. Bằng chứng

- **Nhánh làm việc:** `feat/prompt-versions`
- **Các file sở hữu và chỉnh sửa:**
  - [`starter_v0/artifacts/system_prompt.md`](../../starter_v0/artifacts/system_prompt.md) (Prompt hash cuối: `761e9e9edc38`)
  - [`starter_v0/artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) (Tools hash ở run `v3`: `21ecbe9244ad`, sau khi cập nhật mô tả `hn_search` của C: `c0e6f014aa3b`)
  - [`starter_v0/artifacts/version_log.csv`](../../starter_v0/artifacts/version_log.csv)
  - [`report/team/notes/A_versions.md`](notes/A_versions.md)
- **Các file log đánh giá thực tế (`provider_error_cases = 0`, `measured_cases = 20/20`):**
  - `v0`: [`starter_v0/runs/v0_B_base_gemini_20261110T184728659544.json`](../../starter_v0/runs/v0_B_base_gemini_20261110T184728659544.json) (`v0+pf0c107a9d7a1+t78e3645fdfc4`)
  - `v1`: [`starter_v0/runs/v1_B_base_gemini_20261110T185012798823.json`](../../starter_v0/runs/v1_B_base_gemini_20261110T185012798823.json) (`v1+pefbbdcc86f87+t78e3645fdfc4`)
  - `v2`: [`starter_v0/runs/v2_B_base_gemini_20261110T185216759402.json`](../../starter_v0/runs/v2_B_base_gemini_20261110T185216759402.json) (`v2+p761e9e9edc38+t78e3645fdfc4`)
  - `v3`: [`starter_v0/runs/v3_B_base_gemini_20261110T185438365260.json`](../../starter_v0/runs/v3_B_base_gemini_20261110T185438365260.json) (`v3+p761e9e9edc38+t21ecbe9244ad`)
- **Commit tiêu biểu trên nhánh `feat/prompt-versions`:**
  - `1b5d787`: `feat(prompt): baseline v0 + optimize v1-v3, version_log, notes A`
  - `943a5d3`: `chore(prompt): remove v3.1 run, note hn_search description sync in A_versions`
  - `564f6f6`: `docs(prompt): remove hn_search sync note from A_versions`
- **Công cụ AI đã dùng và cách tự kiểm tra kết quả:**
  - **Công cụ AI hỗ trợ:** Sử dụng trợ lý AI trong IDE (Antigravity) để hỗ trợ đọc hiểu cấu trúc codebase, trích xuất nhanh các trường `observed_mismatch` / `failures` từ file log JSON, và rà soát cú pháp YAML trong `tools.yaml`.
  - **Cách tự kiểm tra (Verification):**
    1. Kiểm tra tính đồng bộ của khai báo tool bằng lệnh `pytest tests/test_tool_contract.py` (đảm bảo 60/60 contract tests luôn pass sau mỗi lần chỉnh sửa `tools.yaml`).
    2. Đối chiếu trực tiếp từng dòng kết quả trong `runs/*.json` (`actual_tool_calls`, `failures`, `summary`) để đảm bảo `provider_error_cases == 0` và `measured_cases == 20` trước khi ghi vào `version_log.csv`.
    3. Quét kiểm tra bảo mật bằng `git diff` và `grep` trước khi commit để đảm bảo không lộ API key hay file `.env` lên repository.

## 5. Tự đánh giá

- **Điểm làm tốt:**
  - Tuân thủ nghiêm ngặt phương pháp tối ưu dựa trên bằng chứng (evidence-driven): mỗi version chỉ thay đổi đúng 1 giả thuyết, giữ nguyên cả kết quả trung thực khi `v1` bị giảm điểm (`0.65` → `0.45`) để phân tích nguyên nhân và sửa đúng điểm nghẽn ở `v2` (`0.45` → `0.75`) và `v3` (`0.75` → `0.85`).
  - Cải thiện `tool_routing_accuracy` từ **0.80 lên 1.00** (routing đúng 20/20 case) và `multiturn_accuracy` từ **0.6667 lên 1.00** (đạt tuyệt đối 6/6 case multi-turn).
- **Bài học rút ra:**
  - Một chỉ dẫn an toàn nếu viết quá cứng nhắc ("không bao giờ đoán handle") sẽ đẩy model sang thái cực ngược lại là *over-clarification* (hỏi lại ngay cả khi thông tin đã đủ rõ). Cần phân biệt rõ giữa "suy diễn vô căn cứ" (đoán bừa một tài khoản khi câu hỏi không nhắc tên ai) và "tri thức thực thể phổ biến" (ánh xạ tên người nổi tiếng đã nêu rõ trong câu hỏi sang handle chuẩn).
  - Việc tách bạch ngữ nghĩa giữa các tham số trong `tools.yaml` (ví dụ: dặn rõ `query` chỉ chứa từ khóa chủ đề vì `topic` và `timeframe` đã biểu đạt ngữ nghĩa tin tức và thời gian) giúp tăng mạnh độ chính xác của arguments.
- **Hạn chế còn tồn đọng ở `v3` (3/20 case chưa pass hoàn toàn về tham số phụ):**
  - `R11_missing_url`: Model đã gọi đúng `clarify` nhưng lược bỏ tham số mặc định `response_type="text"` trong JSON args (`got None`).
  - `R12_confirm_before_send`: Khi người dùng nói *"Đăng bản tin này lên Telegram"* mà chưa kèm nội dung, model ưu tiên hỏi nội dung bản tin (`response_type="text"`) thay vì hỏi xác nhận `yes_no` ngay.
  - `R13_parallel_web_and_tweets`: Khi gọi song song 2 tool trong cùng một lượt, `lookup` vẫn còn sót từ `"AI news"` thay vì `"AI"`.
