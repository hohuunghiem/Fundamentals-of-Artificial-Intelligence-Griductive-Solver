# Fundamentals of Artificial Intelligence – Griductive Solver

> Quy ước phối hợp nhóm 5 người • Bản dự thảo v1.0
>
> Tài liệu này mô tả cách nhóm sẽ triển khai, không khẳng định các chức năng đã hoàn thành. Tên môn trên đề là **Introduction to Artificial Intelligence**; nhóm có thể đổi tiêu đề cho khớp tên môn chính thức.

## 1. Mục tiêu và phạm vi

Xây dựng game Griductive bằng Python, có GUI cho người chơi và bộ giải tự động dùng logic mệnh đề, CNF và DPLL tự cài đặt.

Mỗi ô chứa một nhân vật, một trạng thái thật (tội phạm/vô tội) và một manh mối. Các thẻ được mở ban đầu cung cấp trạng thái và manh mối công khai. Mọi manh mối đều đúng, kể cả của tội phạm. Chỉ được mở thẻ tiếp theo khi trạng thái của nhân vật được chứng minh từ thông tin công khai.

- Nhiều bàn 3×3 và 4×4; 5×5 là tùy chọn để thử tải.
- Đề không ấn định số màn. Nhóm dự kiến 3 bàn 3×3 và 3 bàn 4×4 trước, bổ sung khi cần.
- Mọi màn dùng chung Engine, encoder, DPLL và Agent; không viết công thức hoặc lời giải riêng cho từng màn.
- Không xử lý ngôn ngữ tự nhiên: manh mối được lưu có cấu trúc; GUI tự dựng câu hiển thị.
- Sáu loại manh mối bắt buộc và ít nhất hai mở rộng.
- Có một nghiệm duy nhất với toàn bộ manh mối chưa bảo đảm giải được từng bước từ các thẻ mở ban đầu; phải kiểm tra riêng hai điều này.

Các tên hàm, định dạng dữ liệu, cách chia việc và lịch bên dưới là **quy ước đề xuất của nhóm**, không phải cú pháp bắt buộc từ đề.

## 2. Phân công 5 khối

| Khối | Trách nhiệm chính | Bàn giao |
|---|---|---|
| Game Engine và dữ liệu | Định dạng màn; tải/chơi lại; trạng thái thẻ; bảo vệ thông tin ẩn; xử lý lượt; tạo bộ màn | Engine, các file JSON, kiểm thử luật game |
| CNF encoder | Ánh xạ biến; vùng; 6 loại manh mối và 2 mở rộng; kiểm tra đầu vào; xây KB; semantic evaluator | Encoder, region resolver, kiểm thử tương đương logic |
| DPLL SAT solver | Unit propagation; conflict; chọn biến; phân nhánh/quay lui; phép gán đầy đủ; thống kê | Solver độc lập và kiểm thử SAT/UNSAT |
| Logic Agent và thực nghiệm | Phân loại; kiểm tra verdict; Hint/Auto Solve; trace; kiểm tra nghiệm duy nhất; chạy thực nghiệm | Agent, bộ kiểm tra màn, bảng kết quả |
| GUI và tích hợp | Bàn chơi; nút điều khiển; tô sáng vùng; thông báo; tích hợp; hướng dẫn chạy; video | GUI, hướng dẫn và video demo |

**Khối 2 + 3 + 4 là bộ giải.** Khối 1 quản lý game, khối 5 là giao diện.

Mỗi người viết phần báo cáo và kết quả kiểm thử của mình. Người 4 tổng hợp thực nghiệm; người 1 hỗ trợ bộ màn; người 3 hỗ trợ thống kê. Người 5 tổng hợp định dạng báo cáo, không phải tự viết toàn bộ nội dung.

## 3. Quy tắc kiến trúc

1. Engine sở hữu đáp án và toàn bộ manh mối, kể cả manh mối chưa mở.
2. Agent và encoder khi chơi chỉ nhận `PublicState`; không nhận đường dẫn file màn, `PuzzleData` hay đối tượng Engine để tự truy cập đáp án.
3. DPLL chỉ biết số nguyên và clause; không biết nhân vật, GUI hoặc luật game.
4. GUI gửi thao tác cho Engine; không tự sửa trạng thái và không nhận đáp án ẩn.
5. Engine gọi Agent để kiểm tra verdict. Sau khi được chứng minh, Engine đối chiếu đáp án để phát hiện màn lỗi rồi mới mở thẻ.
6. Auto Solve do controller điều phối: lấy PublicState → gọi Agent → gửi verdict cho Engine → lấy PublicState mới. Agent không gọi ngược Engine, tránh phụ thuộc vòng.
7. Bộ kiểm tra màn ngoại tuyến được đọc toàn bộ dữ liệu; tách khỏi Agent khi chơi và không đưa kết quả ẩn vào Hint.

## 4. Tọa độ, trạng thái và biến

- Cột: A, B, C…; hàng: 1, 2, 3… từ trên xuống.
- Duyệt theo hàng: A1, B1, C1, A2… trên bàn 3×3.
- Mã ô là định danh ổn định; tên và nghề chỉ để hiển thị, trừ khi manh mối quy định rõ.
- Sắp tên nhân vật tăng dần theo thứ tự hiển thị để bám yêu cầu đề.
- `True` là Criminal; `False` là Innocent. JSON dùng `true`/`false`.
- Biến chính: `var_id = (row - 1) * size + column_index`, trong đó A có `column_index = 1`.
- Biến chính từ 1 đến N²; biến phụ bắt đầu từ N² + 1, không trùng nhau.
- Encoder v1 dùng mã hóa tổ hợp trực tiếp nên chưa cần biến phụ, nhưng vẫn báo cáo `aux_count = 0`.
- Thứ tự chọn người của Agent: theo hàng; DPLL chọn biến chưa gán có mã nhỏ nhất, thử True trước rồi False.

## 5. Dữ liệu màn chơi

Mỗi file JSON có các trường bắt buộc:

| Trường | Kiểu | Nội dung |
|---|---|---|
| `schema_version` | integer | Phiên bản định dạng, bắt đầu bằng 1 |
| `puzzle_id` | string | Mã duy nhất, ví dụ `puzzle_3x3_01` |
| `size` | integer | 3, 4 hoặc 5 |
| `characters` | list | N² đối tượng gồm `cell`, `name`, `profession` |
| `solution` | object | Mã ô → boolean; đủ N² ô |
| `clues` | list | N² manh mối; mỗi nhân vật sở hữu đúng một manh mối |
| `initial_revealed` | list[string] | Các ô mở sẵn, không trùng |

Engine phải kiểm tra đủ ô, không trùng mã, tham chiếu hợp lệ và đáp án đầy đủ. Mỗi clue có `id` duy nhất và `owner` là mã ô chứa clue. Tất cả clue phải đúng với `solution`, được kiểm tra bằng semantic evaluator.

## 6. Định dạng manh mối và vùng

Ví dụ đầy đủ cho một manh mối (không phải file màn hoàn chỉnh):

```json
{
  "id": "clue_A1",
  "owner": "A1",
  "type": "EXACTLY",
  "k": 1,
  "region": {"kind": "ROW", "index": 1}
}
```

Các trường dưới đây nằm cùng cấp với `id`, `owner`, `type`:

| Type | Các trường | Nghĩa |
|---|---|---|
| `FACT` | `cell`, `criminal` | Một người có trạng thái xác định |
| `SAME` | `cells`: đúng 2 mã ô khác nhau | Hai người cùng trạng thái |
| `DIFFERENT` | `cells`: đúng 2 mã ô khác nhau | Hai người khác trạng thái |
| `EXACTLY` | `k`, `region` | Đúng k tội phạm |
| `AT_LEAST` | `k`, `region` | Ít nhất k tội phạm |
| `AT_MOST` | `k`, `region` | Nhiều nhất k tội phạm |

| Region | Ví dụ |
|---|---|
| Hàng | `{"kind":"ROW","index":1}` |
| Cột | `{"kind":"COLUMN","label":"B"}` |
| Hàng xóm | `{"kind":"NEIGHBORS","cell":"B2"}` |
| Danh sách ô | `{"kind":"CELLS","cells":["A1","B2"]}` |
| Mở rộng 1: các góc | `{"kind":"CORNERS"}` |
| Mở rộng 2: hàng xóm chung | `{"kind":"COMMON_NEIGHBORS","cells":["A1","C1"]}` |

Quy ước:

- Hàng xóm gồm ngang, dọc, chéo; loại chính ô đang xét.
- Hàng xóm chung là giao hai tập hàng xóm; hai ô tham chiếu phải khác nhau.
- Vùng được trả về theo thứ tự hàng, mỗi ô xuất hiện một lần. Danh sách explicit bị trùng phải báo lỗi đầu vào, không âm thầm sửa.
- `k` phải là số nguyên, không nhận boolean, và 0 ≤ k ≤ số ô trong vùng.
- Vùng rỗng được phép; khi đó chỉ k = 0 hợp lệ và các điều kiện đếm tương ứng đều đúng.
- `NO` hiển thị dưới dạng EXACTLY với k = 0, không thêm một type riêng.
- Hai mở rộng trên là vùng nâng cao theo lựa chọn đề cho phép. Người 1, 2 và 5 cùng hỗ trợ dữ liệu, encoder và hiển thị của chúng.

## 7. Trạng thái công khai

```json
{
  "puzzle_id": "puzzle_3x3_01",
  "size": 3,
  "characters": [
    {"cell":"A1","name":"An","profession":"Bác sĩ"}
  ],
  "known_statuses": {"A1": false},
  "revealed_clues": [
    {
      "id":"clue_A1",
      "owner":"A1",
      "type":"FACT",
      "cell":"B1",
      "criminal":true
    }
  ]
}
```

Ví dụ trên rút gọn danh sách nhân vật để minh họa; dữ liệu thật phải đủ N² người. `known_statuses` và `revealed_clues` phải phản ánh tất cả thẻ đang mở, gồm thẻ mở sẵn. PublicState là bản sao/snapshot, không chứa `solution` hoặc clue chưa mở. Không cho bên nhận sửa trực tiếp state của Engine.

## 8. Giao ước CNF và semantic evaluator

CNF dùng `list[list[int]]`. Ví dụ `[[1,2],[-1,3]]` biểu diễn `(C1 OR C2) AND (NOT C1 OR C3)`.

- Literal dương: tội phạm; literal âm: vô tội; không có literal 0.
- `[1]` là một clause khẳng định C1. `[-1]` khẳng định phủ định C1.
- CNF `[]` là True; CNF `[[]]` là False.
- Thêm trạng thái đã biết bằng unit clause.
- Xây lại KB từ PublicState mỗi bước trong v1 để dễ kiểm tra; không giữ các giả định tạm từ truy vấn trước.
- DPLL không được sửa CNF đầu vào của caller; giả định chỉ tồn tại trong lần gọi tương ứng.

Encoder trả `EncodedKB` gồm `clauses`, `cell_to_var`, `primary_count`, `aux_count`, `num_vars` và `clause_count`. `num_vars = primary_count + aux_count`.

Mã hóa cơ bản:

| Clue | CNF |
|---|---|
| FACT i True | `[[i]]` |
| FACT i False | `[[-i]]` |
| SAME i j | `[[-i,j],[i,-j]]` |
| DIFFERENT i j | `[[i,j],[-i,-j]]` |

Với vùng R có n biến: AT_MOST(k) tạo clause toàn literal âm cho mỗi tập con k+1 biến; AT_LEAST(k) tạo clause toàn literal dương cho mỗi tập con n-k+1 biến; EXACTLY(k) kết hợp cả hai. Xử lý các biên k = 0 và k = n đúng theo định nghĩa; tập con lớn hơn n không tạo clause.

Người 2 cung cấp `evaluate_clue(clue, assignment, board) -> bool`: đánh giá trực tiếp manh mối trên phép gán đầy đủ bằng đếm/so sánh, **không gọi encoder**. Dùng để kiểm tra CNF và dữ liệu màn độc lập.

## 9. Giao ước hàm

Các result record/dataclass đặt trong `models.py`; không tự đổi tên trường giữa các mô-đun.

| Chủ sở hữu | Hàm dự kiến | Kết quả |
|---|---|---|
| Engine | `load_puzzle(path)` | Kiểm tra và khởi tạo màn; trả PublicState |
| Engine | `get_public_state()` | PublicState mới |
| Engine | `restart()` | Trả PublicState ban đầu |
| Engine | `submit_verdict(cell, verdict)` | SubmitResult |
| Encoder | `resolve_region(region, size)` | Danh sách mã ô theo hàng |
| Encoder | `encode(public_state)` | EncodedKB |
| DPLL | `solve(clauses, num_vars)` | SATResult |
| Agent | `classify(public_state, cell)` | ClassificationResult |
| Agent | `classify_all(public_state)` | Kết quả cho mọi người chưa mở, hoặc INCONSISTENT |
| Agent | `next_move(public_state)` | MoveResult |
| Validator | `check_uniqueness(puzzle)` | UNIQUE / MULTIPLE / INCONSISTENT |

Chi tiết kết quả:

- `SATResult`: `status` (SAT/UNSAT), `assignment` (dict[int,bool] hoặc None), `stats`.
- SAT phải trả đủ biến từ 1 đến `num_vars`; biến tự do được điền False nếu công thức đã thỏa mãn. Đây là phép gán thỏa mãn, không có nghĩa biến đó được chứng minh False.
- `ClassificationResult`: `status` (CRIMINAL/INNOCENT/UNKNOWN/INCONSISTENT), `queries`.
- `MoveResult`: `status` (MOVE/SOLVED/STUCK/INCONSISTENT), `cell` và `verdict` (None khi không phải MOVE), `queries`.
- `SubmitResult`: `status`, `public_state`, `revealed_clue` (None nếu không chấp nhận).
- `verdict` tại API là CRIMINAL hoặc INNOCENT; dữ liệu đáp án và known_statuses dùng boolean.

Lỗi thao tác: INVALID_CELL, INVALID_VERDICT, ALREADY_REVEALED. Lỗi dữ liệu màn: `ValueError` có thông báo rõ; GUI bắt lỗi và hiển thị. Không giả vờ các lỗi dữ liệu là UNKNOWN.

## 10. Quy trình suy luận và mở thẻ

1. Encoder tạo KB từ thông tin công khai.
2. Gọi DPLL trên KB. Nếu UNSAT, trả INCONSISTENT và không kết luận bất kỳ người nào.
3. Với người i chưa mở, gọi solver trên bản sao `KB + [[-i]]` và `KB + [[i]]`.
4. Giả định vô tội UNSAT → CRIMINAL; giả định tội phạm UNSAT → INNOCENT; cả hai SAT → UNKNOWN.
5. Agent phân loại các người chưa mở; chọn người chứng minh được đầu tiên theo hàng.
6. Controller gửi kết luận cho Engine. Engine xác minh lại với public state hiện tại.
7. Nếu kết luận được chứng minh và khớp đáp án, trả ACCEPTED, thêm trạng thái, mở đúng thẻ đó và công khai manh mối của nó.
8. Nếu trái trạng thái đã chứng minh: CONTRADICTED. Nếu chưa chứng minh được bên nào: NOT_PROVABLE. Cả hai đều không thay đổi game.
9. Nếu kết luận được chứng minh nhưng không khớp đáp án: PUZZLE_ERROR, không mở thẻ; đây là lỗi dữ liệu cần sửa.
10. Lặp đến SOLVED (đã mở hết), STUCK (còn thẻ nhưng không có nước chứng minh được), hoặc INCONSISTENT.

Hint dùng cùng `next_move`, chỉ hiển thị người và verdict có thể chứng minh; không mở thẻ. Auto Solve thực hiện từng lượt qua Engine, cho phép GUI cập nhật giữa các lượt. Người chơi chọn tay cũng qua cùng cơ chế kiểm tra này.

### Kiểm tra nghiệm duy nhất ngoại tuyến

Mã hóa **toàn bộ manh mối**, có thể thêm trạng thái các thẻ mở ban đầu; tuyệt đối không thêm toàn bộ `solution` thành unit clauses. Nếu UNSAT: INCONSISTENT. Nếu SAT: lấy phép gán đầu tiên, tạo một blocking clause phủ định phép gán trên **các biến nhân vật** (không chặn theo biến phụ), rồi giải lại. Lần hai UNSAT: UNIQUE; SAT: MULTIPLE. Đối chiếu nghiệm với đáp án lưu trong file, và chạy thêm vòng suy luận công khai để kiểm tra khả năng mở thẻ đến hết.

## 11. Trace, thống kê và thực nghiệm

Mỗi bước được chấp nhận ghi: `step`, `active_clue_ids` trước lượt, `sat_queries`, `cell`, `verdict`, `newly_revealed_clue`. Mỗi truy vấn ghi giả định, SAT/UNSAT và thống kê; không ghi manh mối ẩn trước lúc được mở.

Quy ước thống kê DPLL:

- `decisions`: mỗi lần thử gán một giá trị cho biến phân nhánh; không tính unit propagation.
- `propagations`: số biến mới được gán do unit clause; không đếm lại biến đã gán.
- `backtracks`: mỗi lần một nhánh thử thất bại và quyền điều khiển quay về nút cha.
- `runtime_ms`: thời gian một lần solve, đo bằng đồng hồ đơn điệu.
- `sat_calls`: mọi lần gọi solve, kể cả kiểm tra KB và xác minh lại tại Engine; cộng đúng từ các lần gọi thực tế.

Mỗi màn báo cáo: số biến chính/phụ; số clause ban đầu và cuối; số SAT calls; tổng decisions/propagations/backtracks; số lượt mở thêm; thời gian bộ giải đầu-cuối; trạng thái kết thúc. Thời gian đo không gồm animation hoặc thời gian người dùng chờ. Kiểm tra nghiệm duy nhất là phép đo riêng, không cộng vào Auto Solve.

Dùng cùng bộ màn cho mọi so sánh. Nếu đặt timeout, ghi rõ ngưỡng và báo TIMEOUT riêng, không coi là UNSAT. Ghi cả màn thất bại hoặc bị kẹt, không loại khỏi kết quả. Màn thử mâu thuẫn/thiếu thông tin được gắn nhãn là ca kiểm thử, không gọi là màn chơi hợp lệ.

## 12. Cấu trúc dự án dự kiến

| Đường dẫn | Nội dung |
|---|---|
| `Source/main.py` | Điểm khởi chạy và controller |
| `Source/models.py` | Các kiểu dữ liệu dùng chung |
| `Source/engine.py` | Game Engine |
| `Source/regions.py`, `Source/encoder.py`, `Source/semantics.py` | Vùng, CNF và đánh giá trực tiếp |
| `Source/dpll.py` | SAT solver |
| `Source/agent.py` | Suy luận và chọn nước |
| `Source/validator.py` | Kiểm tra màn và nghiệm duy nhất ngoại tuyến |
| `Source/gui/` | Giao diện |
| `Source/puzzles/` | Các file màn JSON |
| `Source/tests/` | Kiểm thử các mô-đun và tích hợp |
| `Source/experiments/` | Script đo và kết quả |
| `Source/requirements.txt` | Thư viện hỗ trợ đã chốt |
| `Source/README.md` | Quy ước nhóm và hướng dẫn chạy |
| `Report.pdf` | Báo cáo kèm URL video |

Lựa chọn GUI v1 đề xuất: Tkinter. Nhóm cần kiểm tra môi trường máy trước khi chốt. Không dùng thư viện SAT thay cho DPLL tự viết. Chưa có mã nguồn trong tài liệu này; lệnh chạy thực tế và phiên bản Python/thư viện phải được bổ sung sau khi tích hợp, không ghi lệnh chưa kiểm chứng là đã chạy được.

