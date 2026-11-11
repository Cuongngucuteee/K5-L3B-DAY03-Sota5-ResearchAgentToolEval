# D - Eval nhóm: ghi chú và bằng chứng B3

## Phạm vi và kết quả

* Thành viên D: Nguyễn Văn Hùng
* Bộ case: `starter\_v0/data/eval\_group.json`, dataset `day03\_v2\_research\_group`.
* Đúng 10 case: 5 single-turn, 5 multi-turn; G01 và G06 kiểm tra tool mới `hn\_search`.
* Provider/model được cấu hình: `gemini` / `gemini-3.5-flash`.
* Version: `v3`; artifact: `v3+padac62a717ee+t952b3d7d4568`.
* Run chính: `starter\_v0/runs/v3\_B\_group\_gemini\_20261111T004453980073.json`.

|Chỉ số|Kết quả|
|-|-:|
|total\_cases|10|
|measured\_cases|10|
|provider\_error\_cases|0|
|passed\_cases|9|
|case\_accuracy|90%|
|tool\_routing\_accuracy|100%|
|argument\_accuracy|90%|
|multiturn\_accuracy|100% (5/5)|

Các tỷ lệ là kết quả của harness, không chứng minh độ chính xác chung của agent ngoài 10 tình huống này. argument\_accuracy là tỷ lệ case có args đạt theo cách chấm của starter, không phải tỷ lệ từng trường tham số.

## B3 - Các case của nhóm

|Case|Mục đích|Tool/args kỳ vọng|Kết quả|
|-|-|-|-|
|G01\_hn\_topic\_and\_limit|Chọn công cụ Hacker News, truyền đúng cụm từ và số lượng; không chấm sort vì chưa có enum chính thức của nhóm.|`hn\_search {"query": "supply chain security", "limit": 4}`|FAIL: query có thêm dấu ngoặc kép|
|G02\_format\_existing\_items|Dùng dữ liệu được cung cấp để định dạng, không gọi công cụ tìm kiếm; cần đọc thủ công args.items để kiểm tra dữ liệu được giữ nguyên.|`format {"template": "bullets", "headline": "Ghi chú nhóm"}`|PASS|
|G03\_social\_latest\_limit|Kiểm tra đồng thời query, Latest và limit; phân biệt bài mới nhất với bài top.|`social\_search {"query": "passkey adoption", "search\_type": "Latest", "limit": 4}`|PASS|
|G04\_missing\_platform|Thiếu nền tảng tìm kiếm và có yêu cầu hỏi trước: không tự chọn Hacker News, X hoặc web.|`clarify {}`|PASS|
|G05\_unsupported\_calendar|Không gọi công cụ research hoặc Telegram để giả lập đặt lịch khi không có công cụ lịch; kiểm tra thủ công câu trả lời có nói rõ giới hạn.|`Không gọi tool`|PASS|
|G06\_hn\_query\_limit\_correction|Cập nhật cả chủ đề và số lượng qua nhiều lượt, vẫn dùng Hacker News; không chấm sort.|`hn\_search {"query": "SQLite", "limit": 2}`|PASS|
|G07\_hn\_to\_web\_month|Đổi nguồn từ Hacker News sang web và mang theo chủ đề, timeframe, số lượng mới.|`lookup {"query": "WebAssembly", "topic": "news", "timeframe": "month", "max\_results": 2}`|PASS|
|G08\_select\_second\_url|Giải quyết tham chiếu link thứ hai trong hai URL; không gọi fetch cho cả hai.|`fetch {"url": "https://docs.python.org/3/library/csv.html"}`|PASS|
|G09\_cancel\_telegram|Tôn trọng việc hủy yêu cầu gửi ở lượt mới nhất; không gọi send hoặc clarify. Case không yêu cầu gửi thật.|`Không gọi tool`|PASS|
|G10\_format\_template\_correction|Nhớ dữ liệu đã có, cập nhật template bullets thành thread và tiêu đề; đọc thủ công args.items để xác minh dữ liệu.|`format {"template": "thread", "headline": "Nhật ký kiểm thử"}`|PASS|

## Phân tích G01 - khác biệt chuỗi query

* Kỳ vọng: `hn\_search(query="supply chain security", limit=4)`.
* Thực tế: tên tool và limit đều đúng; query chứa thêm hai ký tự ngoặc kép ở đầu/cuối: `"supply chain security"`.
* Hàm so sánh starter chuẩn hóa chữ hoa/thường và khoảng trắng đầu/cuối, nhưng không loại dấu ngoặc kép; vì vậy ghi `observed\_mismatch=wrong\_arg\_value`.
* `failure\_counts.wrong\_tool=1` xuất phát từ nhãn failure\_type của case, không chứng minh chọn sai tool. routing\_correct của G01 là true.
* Tool thực thi thành công, trả 4 bài. Điều này không đủ để kết luận query có/không có ngoặc kép tương đương trong mọi trường hợp.
* Giữ nguyên FAIL và metric 90% của run. Không sửa tay run hoặc đổi đáp án sau khi xem kết quả để biến lần chạy này thành PASS.
* Đề xuất gửi A: làm rõ convention query của hn\_search có cho phép thêm dấu ngoặc kép hay phải giữ chuỗi trần; nếu cần chỉnh rubric, tạo revision dataset và chạy đánh giá mới, giữ run cũ.

## Kiểm tra thực thi và nội dung ngoài metric

* G01\_hn\_topic\_and\_limit / hn\_search: không có error dict; trả 4 item.
* G02\_format\_existing\_items / format: không có error dict; item\_count=1.
* G03\_social\_latest\_limit / social\_search: không có error dict; trả 4 item.
* G04\_missing\_platform / clarify: không có error dict; awaiting\_user=True.
* G06\_hn\_query\_limit\_correction / hn\_search: không có error dict; trả 2 item.
* G07\_hn\_to\_web\_month / lookup: không có error dict; trả 2 item.
* G08\_select\_second\_url / fetch: không có error dict; trả 1 item.
* G10\_format\_template\_correction / format: không có error dict; item\_count=1.
* G05: câu trả lời nói rõ không có công cụ truy cập Google Calendar, không giả vờ tạo sự kiện.
* G09: xác nhận đã hủy, không gọi send.
* G02/G10: kiểm tra thủ công args.items cho thấy dữ liệu người dùng được giữ đúng. Tuy nhiên markdown cuối do format trả về không chứa headline đã truyền. Eval PASS chỉ xác nhận đối số.
* Nội dung tìm được và phần văn bản fetch không được đánh giá đầy đủ về độ chính xác, độ mới hay chất lượng tóm tắt. Không đồng nhất routing PASS với hoàn thành toàn bộ yêu cầu người dùng.

## Điều kiện chạy và xử lý lỗi dịch vụ

* Chạy wrapper trong PowerShell: chờ 20 giây trước mỗi lần complete, chỉ retry exception có code 503, tối đa 3 lần retry với khoảng chờ 30/60/120 giây.
* Wrapper không sửa prompt, tools hoặc tiêu chí chấm; không retry dựa trên PASS/FAIL. Kết quả phản ánh lần chạy có chính sách retry lỗi dịch vụ, không phải độ sẵn sàng của lần gọi đầu tiên.

## Lịch sử bộ case và các run trước

* Run `v3\_B\_group\_gemini\_20261110T235740113710.json`: 7/8 case được chấm PASS; 2 provider errors; G03/G08 thiếu key tool. G04 bị FAIL vì kỳ vọng bắt buộc text nhưng agent hỏi lại bằng choice.
* Sửa rubric G04 từ `args={"response\_type":"text"}` thành `args={}` vì yêu cầu hỏi nền tảng cho phép cả câu trả lời tự do lẫn lựa chọn; mục tiêu tự động là gọi clarify. Nội dung câu hỏi và lựa chọn được đọc thủ công. Giữ đúng 10 case; không chỉnh run cũ.
* Run `v3\_B\_group\_gemini\_20261111T002538837198.json`: 7/7 case được chấm PASS; 3 provider errors 503. RapidAPI/Tavily đã trả dữ liệu; G08 chưa gọi Firecrawl vì lỗi model.
* Hai run trên chỉ là bằng chứng chẩn đoán, không dùng làm metric chính thức theo quy định nhóm. Không ghép các case PASS từ nhiều run thành một run mới.
* Run hiện tại có đủ 10 case và 0 provider errors, giữ kết quả 9/10. Không quy mức tăng điểm giữa các run cho tối ưu prompt: rubric G04 và cấu hình API/điều kiện chạy đã thay đổi.

## Giới hạn và việc còn lại

* Multi-turn được harness đưa thành ngữ cảnh văn bản và chỉ chấm lựa chọn ở lượt cuối, đây không phải transcript live chat nhiều lượt thực thi tool.
* G04 args rỗng chỉ chấm tên tool, G05/G09 no\_tool chỉ chấm không gọi tool. Đã đọc thủ công nội dung trong run này, không coi harness tự kiểm tra các nội dung đó.
* D không tự sửa system\_prompt.md, tools.yaml hoặc code tool ngoài phạm vi sở hữu.

## Công cụ AI hỗ trợ

* ChatGPT hỗ trợ soạn 10 case, kiểm tra cấu trúc và cách chấm của starter, phân tích log.

