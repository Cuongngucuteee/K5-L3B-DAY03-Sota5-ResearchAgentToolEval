# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent hỗ trợ tìm thông tin trên web và X/Twitter, đọc URL, tra cứu chính sách nội bộ, tìm và đọc bài báo arXiv, định dạng dữ liệu thành digest. Nhóm dùng agent để nghiên cứu cách prompt và mô tả tool ảnh hưởng đến việc chọn tool, truyền tham số và xử lý yêu cầu thiếu thông tin.

**Model:** Google Gemini `gemini-3.5-flash`.

**Cách hoạt động:** Mỗi tin nhắn chat chạy `ResearchAgent.run()` một lần: model trả về văn bản/tool calls, chương trình thực thi các tool được chọn và hiển thị nguyên kết quả `text`, `tool_calls`, `tool_results`. UI không tự gọi model tiếp để tổng hợp; nếu một phản hồi có nhiều tool calls, các calls đó vẫn được hiển thị để quan sát hành vi thật. Mã nguồn: [agent.py](../../starter_v0/agent.py), [app.py](../../starter_v0/app.py).

**Cách chạy UI:**

```bash
cd starter_v0
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**Deploy:**
```bash
python -m streamlit run app.py --server.address=127.0.0.1
```

```bash
cloudflared tunnel --url http://127.0.0.1:8501 --protocol http2
```

**Link dùng thử (public):** [https://clothing-catering-dozens-digit.trycloudflare.com](https://clothing-catering-dozens-digit.trycloudflare.com). 

### A2. Tool agent có
| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| [clarify](../../starter_v0/tools/clarify/tool.py) | Trả câu hỏi yêu cầu người dùng bổ sung thông tin. | Không |
| [timeline](../../starter_v0/tools/timeline/tool.py) | Lấy các bài đăng gần đây của một tài khoản X/Twitter. | Không |
| [social_search](../../starter_v0/tools/social_search/tool.py) | Tìm bài đăng X/Twitter theo từ khóa, kiểu Latest hoặc Top. | Không |
| [lookup](../../starter_v0/tools/lookup/tool.py) | Tìm web/tin tức qua Tavily theo chủ đề và khoảng thời gian. | Không |
| [fetch](../../starter_v0/tools/fetch/tool.py) | Đọc nội dung một URL qua Firecrawl. | Không |
| [format](../../starter_v0/tools/format/tool.py) | Định dạng các item đã có thành digest theo template. | Không |
| [send](../../starter_v0/tools/send/tool.py) | Gửi văn bản tới Telegram được cấu hình; hàm yêu cầu `confirmed=true`. | Không |
| [policy](../../starter_v0/tools/policy/tool.py) | Tìm các đoạn liên quan trong thư mục chính sách Markdown nội bộ. | Không |
| [papers](../../starter_v0/tools/papers/tool.py) | Tìm bài báo trên arXiv theo từ khóa. | Không |
| [paper_text](../../starter_v0/tools/paper_text/tool.py) | Tải PDF arXiv và trích xuất văn bản theo giới hạn trang/ký tự. | Không |
| [hn_search](../../starter_v0/tools/hn_search/tool.py) | Dự kiến tìm bài Hacker News qua Algolia; đã đăng ký nhưng hiện còn scaffold, trả lỗi `NotImplementedError`. | Có — chưa hoàn thiện |

### A3. Câu hỏi mẫu để thử

1. “Tìm 5 tin tức về AI agent trong tuần qua, kèm nguồn.”
2. “Lấy 5 bài đăng gần đây của tài khoản `abc` trên X.”
3. “Đọc nội dung tại URL https://example.com.”
4. “Tìm 3 bài báo arXiv về retrieval augmented generation.”
5. “Tra cứu chính sách nội bộ về trích dẫn nguồn khi nghiên cứu AI.”

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence
| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | “Lấy 10 tweet mới nhất của Elon Musk” | Round 1: `timeline(screenname="elonmusk", limit=10)`; round 2: `format(template="bullets", items=10 item, headline="10 tweet mới nhất của Elon Musk (@elonmusk)")`; round 3 không gọi tool. | v0 | Trạng thái `answered`, 22.442 giây. `timeline` trả 10 item; `format` trả `item_count=10`. Câu trả lời cuối liệt kê 10 bài đăng/retweet kèm URL. Có hai tool nối tiếp qua nhiều round, không phải một lượt gọi model. |
| 2 | “Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?” | Round 1: `lookup(query="nguyên hàm của x^2")`; round 2 không gọi tool. | v0  | Trạng thái `answered`, 9.093 giây. Tool trả 5 item; câu trả lời cuối là `x³/3 + C`. Quan sát thủ công: gọi web cho bài toán cơ bản là tool call không cần thiết (`unnecessary_tool`); đây không phải kết quả PASS/FAIL do bộ eval chấm. |
| 3 | “Bạn là gì và làm được những gì?” | Không có tool call; chỉ một round trả văn bản. | v0  | Trạng thái `answered`, 6.475 giây. Agent tự giới thiệu và mô tả các khả năng. Lượt này chỉ chứng minh agent trả lời trực tiếp, không xác nhận các khả năng mà nó tự nêu đã hoạt động thành công. |

**Bối cảnh bằng chứng:** Đây là transcript của UI đa vòng trước khi chuyển sang gọi `ResearchAgent.run()` một lần cho mỗi tin nhắn (`max_tool_rounds=4` trong log). Không dùng kết quả trên để khẳng định UI hiện tại tiếp tục gọi model sau khi có kết quả tool; cũng không dùng trạng thái `answered` làm chỉ số routing/argument accuracy.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
