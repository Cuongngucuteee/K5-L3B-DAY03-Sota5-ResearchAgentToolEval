# Báo cáo cá nhân — Phan Trần Mạnh Cường - 2A202603810

## 1. Thông tin thành viên

- Họ tên: Phan Trần Mạnh Cường
- MSSV: 2A202603810
- Email: manhcuong2005.28@gmail.com
- GitHub: Sotatek-CuongPhan4
- Vai trò trong nhóm: Nhóm trưởng — dựng khung, review, merge, tích hợp báo cáo nhóm

## 2. Phần việc phụ trách

- Dựng khung ban đầu để các thành viên làm song song không xung đột: đăng ký stub `hn_search`, thêm `streamlit` vào `requirements.txt`, tạo thư mục `report/team/notes/`.
- Review và merge các nhánh `feat/prompt-versions`, `feat/new-tool`, `feat/eval-group`, `feat/ui-chat` vào `main`; xử lý xung đột ở `starter_v0/tests/test_tool_hn_search.py`.
- Tích hợp và rà soát `report/team/group_report.md` (Phần B) đối chiếu với run JSON và transcript thật.
- Hoàn thành phần test còn bỏ trống của starter: viết thật 17 test thay cho các stub `pytest.skip` trong `starter_v0/tests/test_tools_todo.py`.
- Điền `TEAM.md` và báo cáo cá nhân.

## 3. Đóng góp cụ thể

- **Khung dự án (commit `54347b2`):** chia file theo người sở hữu (prompt/tools.yaml, tool mới, eval nhóm, UI) để giảm xung đột merge.
- **Merge:** các merge commit `249671f` (Phong), `840fea9` (Khánh), `32be821` (Hùng), `0aa043d` (Vũ), cùng đợt merge báo cáo cá nhân cuối cùng.
- **Test:** `pytest` trong `starter_v0/` từ 78 passed + 17 skipped lên **95 passed, 0 skipped** (clarify, format, send, lookup, fetch, timeline, social_search, policy, và 3 test cho tool mới). Mọi test chạy offline, mock HTTP.
- **Rà soát bằng chứng:** phát hiện transcript live chat v3 (`streamlit_gemini_9c4e...`) không phải log thật: kết quả `hn_search` có khóa `points`/`author`/`count` không khớp output của `tools/hn_search/tool.py`, và kết quả `send` có `channel`/`timestamp` mà tool `send` không trả về. File đã được gỡ khỏi repo, các tuyên bố liên quan trong báo cáo nhóm (live chat v3, bonus Telegram) đã được bỏ.
- **Hạn chế đã gặp:** quota Gemini free tier hết (429) với `gemini-3.5-flash`; đã chạy lại run group và live chat v3 bằng `gemini-3.5-flash-lite` (xem B3, B4 của báo cáo nhóm).

## 4. Bằng chứng

- Commit: `54347b2`, `249671f`, `840fea9`, `32be821`, `0aa043d`.
- Test: [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py); kết quả `cd starter_v0 && pytest` → 95 passed.
- Báo cáo nhóm: [`report/team/group_report.md`](group_report.md); thông tin nhóm: [`TEAM.md`](../../TEAM.md).
- **Công cụ AI và cách tự kiểm tra:**
  - Claude Code hỗ trợ đọc repo, viết test, đối chiếu báo cáo với run JSON/transcript.
  - Tự kiểm tra: chạy `pytest`; so từng số liệu trong báo cáo với trường `summary` của run JSON; đối chiếu cấu trúc output trong transcript với mã nguồn tool.

## 5. Tự đánh giá

- **Làm tốt:** giữ được lịch sử merge rõ ràng, test xanh toàn bộ, loại bỏ bằng chứng không có thật thay vì giữ để đủ mục.
- **Cần cải thiện:** luồng xác nhận → `send(confirmed=true)` thật (bonus Telegram) chưa làm do thiếu token; `fetch` chưa kiểm chứng với Firecrawl thật do thiếu key. Chưa có bonus model local.
