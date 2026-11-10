# A — Prompt & Version (ghi chú)

Model: `gemini-3.5-flash-lite` (provider `gemini`), cố định cho v0–v3. Suite: `base` (20 case).
Lưu ý kỹ thuật: Free Tier giới hạn 15 req/phút → chạy qua wrapper throttle (~4.5s/request) + retry khi 429/503. Wrapper không sửa repo; kết quả là phản hồi thật của model. Hai run đầu của v0 (model `gemini-3.5-flash` và `gemini-3.5-flash-lite` lần 1) bị `provider_error` (429/503) nên **không dùng làm bằng chứng** và đã loại khỏi `runs/`. Các run dưới đây đều có `provider_error_cases = 0`, `measured_cases = 20`.

## B1 — Bảng version

| Version | Giả thuyết (1 thay đổi) | File sửa | case_acc | routing_acc | arg_acc | multiturn_acc | Run file |
|---|---|---|---|---|---|---|---|
| v0 | Baseline | — | 0.65 | 0.80 | 0.65 | 0.6667 | `runs/v0_B_base_gemini_20261110T184728659544.json` |
| v1 | 3 chỉ dẫn xấu (đoán / gửi không xác nhận / ép một bước) gây missing_info + wrong_boundary + wrong_tool | system_prompt.md | 0.45 | 0.65 | 0.45 | 0.1667 | `runs/v1_B_base_gemini_20261110T185012798823.json` |
| v2 | Rule hỏi lại của v1 quá rộng → hạn chế clarify, dùng handle quen thuộc cho người nổi tiếng | system_prompt.md | 0.75 | 1.00 | 0.75 | 0.6667 | `runs/v2_B_base_gemini_20261110T185216759402.json` |
| v3 | tools.yaml thiếu convention args → viết lại description + convention | tools.yaml | 0.85 | 1.00 | 0.85 | 1.00 | `runs/v3_B_base_gemini_20261110T185438365260.json` |

Nhận xét: v1 **làm tệ hơn** v0 (0.65 → 0.45) — đây là kết quả thật, giữ nguyên trong log. Nguyên nhân đọc từ run: rule "không bao giờ đoán handle" làm model hỏi handle của Sam Altman / Elon Musk (R01, R05, M01, M03, M05). v2 sửa đúng điểm này.

## B2 — Failure analysis

### v0 (13/20 pass)

| Case | Loại lỗi | Quan sát thật | Nguyên nhân giả định |
|---|---|---|---|
| R10_missing_handle | missing_info | gọi `timeline(screenname=sama)` thay vì `clarify` | prompt bảo "đoán, đừng hỏi" |
| R11_missing_url | missing_info | gọi `lookup` thay vì `clarify` | prompt bảo "đoán URL" |
| R12_confirm_before_send | wrong_boundary | gọi `send(confirmed=true)` ngay | prompt bảo "cứ gửi luôn" |
| R13_parallel_web_and_tweets | wrong_tool | chỉ gọi `lookup`, thiếu `social_search` | prompt ép "một bước, một tool" |
| R03, M02, M06 | wrong_tool / wrong_arg_value | `query` thừa từ ("AI news today", "robotics news today", "OpenAI news") | thiếu convention `query` |

### v3 (17/20 pass) — còn lỗi

| Case | Loại lỗi | Quan sát thật | Ghi chú |
|---|---|---|---|
| R11_missing_url | missing_info | gọi `clarify` đúng nhưng không truyền `response_type` (expected `text`) | model bỏ qua tham số optional |
| R12_confirm_before_send | wrong_boundary | `clarify(response_type=text)` hỏi nội dung bản tin, expected `yes_no` | user chưa đưa nội dung nên model hỏi nội dung, chưa chuyển sang xác nhận |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(query="AI news")`, expected `AI` | convention `query` chưa đủ mạnh trong ca song song |

## v3.1 — đồng bộ mô tả hn_search (không phải vòng tối ưu)
Sau khi C gửi mô tả `hn_search`, A cập nhật `tools.yaml` (đổi `tools_hash` → `c0e6f014aa3b`) và chạy lại để artifact khớp run.
Run: `runs/v3.1_B_base_gemini_20261110T185713752681.json` — 0 provider_error, case_acc 0.85, routing 1.00, multiturn 1.00 (cùng metric với v3).

Lỗi còn lại ở v3.1: R03 (`query`="AI artificial intelligence news", expected `AI`), R11 và R12 (`clarify` không truyền `response_type`).

Quan sát: metric tổng giữ 0.85 nhưng **tập case lỗi đổi** (R13 đạt, R03 lỗi) dù chỉ sửa mô tả `hn_search` không liên quan. Nghĩa là model có độ dao động giữa các lần chạy dù `temperature=0`; sai khác 1 case (0.05) giữa hai run không nên được xem là cải thiện hay tụt thật.

## Việc còn tồn
- 3 case còn lỗi ở v3.1 có thể xử lý nếu cần thêm một vòng (ngoài yêu cầu tối thiểu v1–v3).
