# Báo cáo cá nhân — Nguyễn Nam Khánh - 2A202603871

## 1. Thông tin thành viên

- Họ tên: Nguyễn Nam Khánh
- MSSV: 2A202603871
- Email: 26ai.khanhnn3@vinuni.edu.vn

## 2. Phần việc phụ trách

Phần việc của tôi tập trung vào tạo giao diện để người dùng chat với agent, quan sát trực tiếp cách model chọn tool và xem kết quả thực thi. Giao diện dùng Google Gemini `gemini-3.5-flash`, đọc system prompt và tool declarations từ các artifact của nhóm.

Ngoài chat, UI hỗ trợ chạy từng eval case hoặc toàn bộ dataset, hiển thị kết quả chấm điểm và xuất JSON. Tôi cũng tham gia chuẩn bị cách truy cập demo qua Cloudflare Tunnel và bổ sung phần giới thiệu agent, bằng chứng live chat trong báo cáo nhóm. Các phần triển khai và tài liệu được thực hiện với sự hỗ trợ của Codex; cách kiểm tra được ghi tại mục 4.

## 3. Đóng góp cụ thể

### 3.1. Xây dựng giao diện chat

- Tạo [app.py](https://github.com/Cuongngucuteee/K5-L3B-DAY03-Sota5-ResearchAgentToolEval/blob/ed8219f592025e77311b95fba4525102396f520a/starter_v0/app.py) bằng Streamlit, có hai chế độ **Chat** và **Dataset evaluation** trong sidebar.
- Hiển thị văn bản trả lời cùng toàn bộ `text`, `tool_calls`, `tool_results`, giữ nguyên kết quả agent để có thể kiểm tra tool và arguments thay vì chỉ nhìn câu trả lời cuối.
- Lưu lịch sử bằng session state, hỗ trợ tiếp tục hội thoại, bắt đầu chat mới, lưu transcript xuống thư mục `transcripts/` và tải JSON.
- Hiển thị lỗi provider, vô hiệu hóa gửi yêu cầu khi thiếu Gemini API key, và che giá trị biến môi trường chứa key/token trong lỗi chat.

### 3.2. Bổ sung kiểm thử dataset trên UI

- Thêm chọn dataset và case, nút **Run selected case**, nút **Run entire dataset**, cùng thanh tiến độ khi chạy batch.
- Mỗi eval case chạy độc lập với lịch sử chat. UI tái sử dụng các hàm xử lý input, chấm điểm và tổng hợp của evaluator, gồm `case_messages`, `evaluate_phase_b`, `summarize`, `print_table`.
- Đặt phần điều phối `run_case()` và `run_cases()` trong `app.py`, không yêu cầu thêm helper vào `run_eval.py`.
- Hiển thị PASS/FAIL, lỗi routing/arguments, raw tool results và summary; lưu kết quả vào `runs/` và cho tải JSON. Khi một case lỗi provider, batch ghi nhận lỗi và tiếp tục các case còn lại.

### 3.3. Chuẩn bị demo và tài liệu

- Thiết lập truy cập public bằng Cloudflare Tunnel và bổ sung cách khởi chạy trên máy khác.
- Bổ sung Phần A của [báo cáo nhóm]: giới thiệu agent, cách chạy UI, danh sách tool và câu hỏi mẫu.
- Điền bảng B4 từ các lượt 1–3 của transcript.
## 4. Bằng chứng

| Nội dung | Bằng chứng | Cách đối chiếu |
|---|---|---|
| Chat và chạy eval trên UI | [app.py](https://github.com/Cuongngucuteee/K5-L3B-DAY03-Sota5-ResearchAgentToolEval/blob/ed8219f592025e77311b95fba4525102396f520a/starter_v0/app.py) | Xem `render_chat`, `render_evaluation`, `run_case`, `run_cases`; model cố định và một lần `ResearchAgent.run()` cho mỗi yêu cầu/case. |
| Kiểm thử giao diện trong phiên làm việc | Mô tả và kết quả được ghi trực tiếp bên dưới. | 7 test offline kiểm tra case đơn, batch và lỗi provider, nhiều tool calls trong một phản hồi, thiếu key, lỗi ghi file, chat/history và tách biệt chat với eval. File test này chưa được đưa lên upstream. |
| Kết quả kiểm tra toàn suite trong phiên làm việc | Trích kết quả pytest trực tiếp trong báo cáo. | **74 passed, 17 skipped**; 17 test skipped là các TODO trong `test_tools_todo.py`. Kết quả gồm các test UI chưa có trên upstream; không phải kết quả CI hoặc metric độ chính xác của model. |
| Live chat và phân tích hành vi | [Transcript Streamlit](https://github.com/Cuongngucuteee/K5-L3B-DAY03-Sota5-ResearchAgentToolEval/blob/ed8219f592025e77311b95fba4525102396f520a/starter_v0/transcripts/streamlit_gemini_39928a349ae4459980c834521347f10f.transcript.json) | Các lượt 1–3 được tóm tắt tại B4; log ghi tool calls, results, thời gian và prompt/tool hashes của UI cũ. |

**AI/công cụ đã dùng và cách kiểm tra:**

- **Codex:** hỗ trợ đọc cấu trúc repo, viết và chỉnh sửa UI, tạo test, phân tích transcript, soạn tài liệu. Tôi đưa yêu cầu, rà soát hướng tích hợp và yêu cầu sửa khi UI chưa phản ánh đúng cách chạy agent, khi mất phần chat hoặc khi helper bị đặt vào evaluator.
- **Streamlit AppTest và pytest:** kiểm tra hành vi UI bằng model response giả lập và tool giả lập; không gọi API thật trong các test này. Đối chiếu cấu trúc output và summary với các hàm evaluator có sẵn.
- **Kiểm tra trực tiếp:** trong phiên làm việc đã chạy preflight Gemini thành công với `gemini-3.5-flash`, kiểm tra public page và health endpoint trả HTTP 200, đồng thời kết nối được WebSocket qua tunnel. Các kiểm tra này xác nhận kết nối tại thời điểm thực hiện, không chứng minh mọi tool hoặc mọi eval case đều thành công.
- **Đối chiếu log thật:** kiểm tra input, tool calls và kết quả trong transcript trước khi đưa vào báo cáo; không dùng trạng thái `answered` để suy ra PASS/FAIL hay tự tạo số liệu v0–v3.

## 5. Tự đánh giá

**Đánh giá theo sản phẩm và bằng chứng:** Phần UI đã có chat, hiển thị raw agent output, kiểm thử từng case và batch, lưu/tải kết quả, cùng hướng dẫn demo public.

**Điểm cần cải thiện:** UI ban đầu chọn vòng lặp chat đa bước chưa phù hợp với mục tiêu quan sát agent single-pass; phần này đã được điều chỉnh sau khi đối chiếu với yêu cầu. Việc dùng cùng provider, prompt và tool declarations chưa đủ để đảm bảo hai giao diện có hành vi tương đương: còn phải kiểm tra cách tạo messages, số lần gọi model và cách xử lý tool results. Helper chạy case thuộc phạm vi UI cần đặt tại `app.py` để không làm thay đổi evaluator của nhóm.

**Giới hạn hiện tại:** Test giả lập không thay cho đánh giá chất lượng model qua API thật. UI chưa có xác thực người dùng hoặc giới hạn quota cho demo public; URL tunnel không cố định.