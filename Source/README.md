# Griductive Solver

Griductive Solver là trò chơi suy luận logic được xây dựng bằng Python và Tkinter. Chương trình gồm 9 màn chơi với các kích thước 3×3, 4×4 và 5×5, hỗ trợ chơi thủ công và giải tự động bằng logic mệnh đề, CNF và thuật toán DPLL SAT Solver.

Dự án được thực hiện trong học phần **CSC14003 - Cơ sở Trí tuệ Nhân tạo**.

## 1. Yêu cầu hệ thống

- Python 3.10 trở lên.
- Các thư viện được liệt kê trong `requirements.txt`.
- Hệ điều hành Windows, Linux hoặc macOS có hỗ trợ Python và Tkinter.

Các thành phần chính:

- `tkinter`: Xây dựng giao diện trò chơi.
- `CNF Encoder`: Chuyển đổi manh mối thành công thức logic dạng CNF.
- `DPLL SAT Solver`: Giải bài toán SAT/UNSAT.
- `Logic Agent`: Suy luận trạng thái nhân vật và điều khiển quá trình giải tự động.

Các thuật toán chính được nhóm tự cài đặt, không sử dụng thư viện SAT Solver có sẵn.

## 2. Cài đặt và chạy chương trình

Mở terminal tại thư mục `Source`, nơi chứa `main.py` và `requirements.txt`.

### 2.1. Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### 2.2. Windows CMD

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python main.py
```

### 2.3. Linux và macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Những lần chạy tiếp theo chỉ cần kích hoạt môi trường và thực thi:

```bash
python main.py
```

Có thể mở trực tiếp một màn chơi bằng:

```bash
python main.py --puzzle puzzles/level_4x4_hard.json
```

## 3. Điều khiển trò chơi

| Nút | Chức năng |
|---|---|
| CHỌN MÀN CHƠI | Mở danh sách màn chơi |
| LUẬT CHƠI | Xem hướng dẫn và luật chơi |
| BẮT ĐẦU | Bắt đầu màn đã chọn |
| TỘI PHẠM | Kết luận nhân vật được chọn là tội phạm |
| VÔ TỘI | Kết luận nhân vật được chọn là vô tội |
| LOAD | Nạp màn chơi từ file JSON |
| RESTART | Khởi động lại màn hiện tại |
| HINT | Gợi ý một kết luận có thể chứng minh |
| AUTO SOLVE | Tự động giải màn chơi |
| STOP | Dừng quá trình tự động giải |
| CHỌN MÀN | Quay về danh sách màn chơi |

Người chơi chọn một nhân vật trên bàn cờ và đưa ra kết luận. Nếu kết luận được chứng minh bằng thông tin công khai, thẻ sẽ mở và tiết lộ manh mối mới.

Các kết luận chưa thể chứng minh hoặc trái với thông tin đã biết sẽ bị từ chối.

## 4. Hệ thống suy luận logic

Chương trình sử dụng ba thành phần chính:

- **CNF Encoder:** Chuyển các manh mối và trạng thái đã biết thành công thức CNF.
- **DPLL SAT Solver:** Kiểm tra công thức có thỏa mãn hay không bằng unit propagation, branching và backtracking.
- **Logic Agent:** Sử dụng CNF và DPLL để chứng minh trạng thái nhân vật, cung cấp Hint và Auto Solve.

Sáu loại manh mối bắt buộc:

| Clue | Ý nghĩa |
|---|---|
| FACT | Một nhân vật có trạng thái xác định |
| SAME | Hai nhân vật có cùng trạng thái |
| DIFFERENT | Hai nhân vật có trạng thái khác nhau |
| EXACTLY | Chính xác k tội phạm trong một vùng |
| AT_LEAST | Ít nhất k tội phạm trong một vùng |
| AT_MOST | Nhiều nhất k tội phạm trong một vùng |

Các vùng hỗ trợ gồm `ROW`, `COLUMN`, `NEIGHBORS`, `CELLS` và hai vùng mở rộng `CORNERS`, `COMMON_NEIGHBORS`.

Logic Agent chỉ nhận thông tin công khai (`PublicState`), không được truy cập đáp án ẩn hoặc manh mối chưa mở.

## 5. Các màn chơi

Chương trình có 9 màn được lưu trong thư mục `puzzles/`.

| Màn chơi | File |
|---|---|
| 3×3 Easy | `demo_3x3.json` |
| 3×3 Medium 1 | `level_3x3_medium_01.json` |
| 3×3 Medium 2 | `level_3x3_medium_02.json` |
| 4×4 Easy | `demo_4x4.json` |
| 4×4 Medium | `level_4x4_medium.json` |
| 4×4 Hard | `level_4x4_hard.json` |
| 5×5 Medium 1 | `level_5x5_medium.json` |
| 5×5 Medium 2 | `level_5x5_medium_02.json` |
| 5×5 Hard | `level_5x5_hard.json` |

Hai màn Easy dùng để làm quen với trò chơi. Các màn Medium và Hard kết hợp nhiều loại manh mối, yêu cầu suy luận qua nhiều bước.

Các màn nâng cao đã được kiểm chứng độc lập về nghiệm duy nhất và khả năng giải không đoán; cần kiểm thử lại bằng Logic Agent chính thức sau khi hoàn thiện.

## 6. Kiểm thử và thực nghiệm

Mở terminal tại thư mục `Source`.

Kiểm thử toàn bộ chương trình:

```bash
python -m unittest discover -s tests -v
```

Kiểm thử riêng Logic Agent:

```bash
python -m unittest tests.test_logic_agent -v
```

Các chỉ số cần ghi nhận khi thực nghiệm gồm:

- Primary Variables và Auxiliary Variables.
- CNF Clauses.
- SAT Calls.
- Decisions, Propagations và Backtracks.
- Deduction Steps.
- Runtime.
- Trạng thái kết thúc: SOLVED, STUCK hoặc INCONSISTENT.

Kết quả thực nghiệm được tổng hợp sau khi CNF Encoder, DPLL và Logic Agent hoàn thiện.

## 7. Cấu trúc mã nguồn

```text
Source/
├── main.py
├── models.py
├── engine.py
├── controller.py
├── regions.py
├── semantics.py
├── requirements.txt
├── README.md
├── algorithm/
│   ├── __init__.py
│   ├── encoder.py
│   ├── dpll.py
│   ├── agent.py
│   └── validator.py
├── gui/
│   ├── __init__.py
│   ├── menu.py
│   ├── app.py
│   ├── board.py
│   ├── formatting.py
│   └── theme.py
├── puzzles/
│   ├── demo_3x3.json
│   ├── demo_4x4.json
│   ├── level_3x3_medium_01.json
│   ├── level_3x3_medium_02.json
│   ├── level_4x4_medium.json
│   ├── level_4x4_hard.json
│   ├── level_5x5_medium.json
│   ├── level_5x5_medium_02.json
│   └── level_5x5_hard.json
├── tests/
│   ├── test_core.py
│   └── test_logic_agent.py
└── experiments/
    └── run_experiments.py
```

Chức năng các thành phần:

- `main.py`: Khởi chạy trò chơi và khởi tạo Logic Agent.
- `engine.py`: Quản lý màn chơi, trạng thái và đáp án ẩn.
- `controller.py`: Điều phối thao tác giữa GUI và Game Engine.
- `models.py`: Định nghĩa các kiểu dữ liệu và kết quả dùng chung.
- `regions.py`, `semantics.py`: Xử lý vùng và đánh giá manh mối.
- `algorithm/`: CNF Encoder, DPLL Solver, Logic Agent và Validator.
- `gui/`: Giao diện trang chủ, chọn màn, luật chơi và bàn cờ.
- `puzzles/`: Dữ liệu JSON của 9 màn chơi.
- `tests/`: Kiểm thử Core Game và Logic Agent.
- `experiments/`: Thực hiện các thí nghiệm đánh giá thuật toán.

## 8. Trạng thái và thông tin dự án

**Học phần:** CSC14003 - Cơ sở Trí tuệ Nhân tạo

**Tên đồ án:** Griductive Solver – Project 2

**Ngôn ngữ:** Python

**Giao diện:** Tkinter

**Thuật toán:** CNF Encoding, DPLL SAT Solver, Deductive Logic Agent

**Trạng thái hiện tại:**

- Core Game, GUI và dữ liệu màn chơi đã được xây dựng.
- Chương trình đã chuyển sang sử dụng `LogicAgent` chính thức.
- CNF Encoder, DPLL Solver, Logic Agent và Validator đang được các thành viên tiếp tục triển khai.
- Các thao tác suy luận chưa thể hoạt động đầy đủ trước khi tích hợp xong thuật toán.

Các thành viên cần giữ nguyên hợp đồng API trong `models.py` và bảo đảm Agent không truy cập thông tin ẩn của Game Engine.