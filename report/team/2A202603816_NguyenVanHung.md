# Báo cáo cá nhân — NguyenVanHung-2A202603816

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Hùng
- MSSV: 2A202603816
- Email:

## 2. Phần việc phụ trách

Phụ trách phần D - Eval nhóm, làm việc trên nhánh `feat/eval-group`. Nhiệm vụ chính là xây dựng đúng 10 tình huống đánh giá trong `starter_v0/data/eval_group.json`, gồm 5 single-turn và 5 multi-turn, có case kiểm tra tool mới `hn_search`, chạy group eval bằng prompt/tools của A và ghi nhận kết quả để nhóm tổng hợp bảng B3.


## 3. Đóng góp cụ thể

- Xây dựng bộ 10 case, giữ cấu trúc dataset của nhóm và bổ sung các trường `id`, `phase`, `failure_type`, `expect`, `metadata.what_it_tests`.
- Thiết kế các tình huống chọn nguồn tìm kiếm, truyền tham số, hỏi lại khi thiếu nền tảng, yêu cầu ngoài phạm vi, cập nhật chủ đề/số lượng qua nhiều lượt, chọn URL, hủy gửi Telegram và sửa kiểu định dạng.
- Chạy kiểm tra cấu trúc và đăng ký tool, xác nhận đủ 10 case, gồm 5 single-turn và 5 multi-turn.
- Đối chiếu kỳ vọng với khai báo tool của nhóm, cấu hình API trên máy cá nhân và kiểm tra trực tiếp `social_search` trả dữ liệu.
- Chạy group eval bằng Gemini với prompt/tools v3. Đọc run JSON để phân biệt lỗi routing/args, lỗi provider và lỗi thực thi tool.
- Điều chỉnh rubric G04: ban đầu yêu cầu `response_type="text"`, trong khi agent hỏi lại bằng `choice` vẫn đúng mục tiêu. Bỏ ràng buộc kiểu trả lời trong kỳ vọng, giữ yêu cầu gọi `clarify` và kiểm tra nội dung hỏi lại thủ công. Không sửa các run cũ.
- Xử lý điều kiện chạy khi gặp lỗi 429/503 bằng wrapper PowerShell: chờ 20 giây trước mỗi lần gọi model, chỉ retry lỗi 503, tối đa 3 lần với khoảng chờ 30/60/120 giây. Không sửa prompt, harness hoặc điểm trong run.
- Tổng hợp bảng B3, phân tích case FAIL và giới hạn bộ chấm vào `report/team/notes/D_eval.md`.

## 4. Bằng chứng

- Bộ case: `starter_v0/data/eval_group.json`.
- Ghi chú và bảng B3: `report/team/notes/D_eval.md`.
- Báo cáo cá nhân: `report/team/2A202603816_NguyenVanHung.md`.
- Run chính: `starter_v0/runs/v3_B_group_gemini_20261111T004453980073.json`.
- Run chẩn đoán trước đó:
    -`starter_v0/runs/v3_B_group_gemini_20261110T235740113710.json`: 2 provider errors, G04 có kỳ vọng quá chặt, một số tool thiếu key.
    -`starter_v0/runs/v3_B_group_gemini_20261111T002538837198.json`: 3 provider errors 503.
    - Hai run chẩn đoán không dùng làm kết quả đánh giá chính thức, không ghép các case PASS giữa nhiều run.
- Version: `v3`.
- Artifact version: `v3+padac62a717ee+t952b3d7d4568`.
- Provider/model được cấu hình: `gemini` / `gemini-3.5-flash`.
- Commit nhánh `feat/eval-group`

- Công cụ/AI và cách tự kiểm tra kết quả: 
    - ChatGPT: Hỗ trợ hiểu đề, xây dựng case, phân tích lỗi, sửa báo cáo.
    - Gemini API Model được đánh giá qua các yêu cầu thật, ghi nhận lỗi dịch vụ và kết quả sau retry.


## 5. Tự đánh giá

Tôi đã hoàn thành việc xây dựng bộ eval và có lần chạy đầy đủ 10 case, không còn lỗi provider cuối cùng. Bộ kiểm tra phát hiện được khác biệt tham số ở G01 và giúp phân biệt lỗi model với lỗi cấu hình API, lỗi dịch vụ cũng như hạn chế của tiêu chí chấm.
Điểm cần cải thiện là thiết kế rubric rõ ngay từ đầu: G04 ban đầu ràng buộc kiểu hỏi lại quá chặt, còn G01 cần thống nhất cách hiểu dấu ngoặc kép trong truy vấn. Tỷ lệ 90% chỉ phản ánh 10 case và phạm vi chấm hiện tại, không phải đánh giá tổng quát độ tin cậy của agent.

