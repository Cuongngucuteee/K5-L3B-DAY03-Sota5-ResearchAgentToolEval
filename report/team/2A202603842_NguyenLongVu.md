# Báo cáo cá nhân — HoVaTen-MSSV

## 1. Thông tin thành viên

- Họ tên: Nguyễn Long Vũ
- MSSV: 2A202603842
- Email: nguyenlongvu17082004@gmail.com

## 2. Phần việc phụ trách

Tạo tool mới và xây dựng các test cases

## 3. Đóng góp cụ thể

Tạo tool hn_search:
- Tool hn_search cho phép tìm kiếm các bài viết, câu hỏi và thảo luận trên Hacker News thông qua Algolia API công khai. 
- Nó hỗ trợ tùy chỉnh sắp xếp theo độ liên quan hoặc thời gian mới nhất, đồng thời tự động chuẩn hóa và làm sạch dữ liệu kết quả. 
- Tool tích hợp xác thực tham số đầu vào và cơ chế bắt lỗi an toàn, trả về từ điển lỗi thay vì làm gián đoạn chương trình khi xảy ra sự cố mạng.

Tạo các test case cho tool mới:
- Test happy path, thiếu dữ liệu đầu vào, lỗi kết nối. Thêm các test case khác như limit sai kiểu dữ liệu.
- Chạy thành công test case không lỗi.

## 4. Bằng chứng

- File/commit/PR:
K5-L3B-DAY03-Sota5-ResearchAgentToolEval\starter_v0\tools\hn_search\tool.py
K5-L3B-DAY03-Sota5-ResearchAgentToolEval\starter_v0\tests\test_tool_hn_search.py
Pass all test case: đã chạy pytest và pytest tests/test_tool_contract.py đều không có lỗi

- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
Sử dụng Gemini để fix lỗi code và đưa thêm ví dụ test cases.

## 5. Tự đánh giá
- Đánh giá theo sản phẩm và bằng chứng: Đã hoàn thiện và tích hợp thành công công cụ mới hn_search (search_hacker_news), cấu hình kết nối chuẩn xác với Algolia API, đồng thời viết toàn bộ unit test đạt 9/9 PASS.

- Đảm bảo xử lý chặt chẽ việc chuẩn hóa tham số đầu vào và cơ chế bắt lỗi ngoại lệ trả về error dict nhằm tránh làm gián đoạn chương trình.

- Các bài test sử dụng mocking (_patch_urlopen) nên chưa kiểm thử độ ổn định thực tế với mạng ngoài; kết quả đánh giá phụ thuộc vào phản hồi từ Algolia API công khai.
...
