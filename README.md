# Griductive Solver

Griductive Solver là trò chơi suy luận logic được xây dựng bằng Python và Tkinter. Chương trình gồm 9 màn chơi với các kích thước 3×3, 4×4 và 5×5, hỗ trợ chơi thủ công và giải tự động bằng logic mệnh đề, CNF và thuật toán DPLL SAT Solver.

Dự án được thực hiện trong học phần **CSC14003 - Cơ sở Trí tuệ Nhân tạo**.

## Nhóm 8 — Thành viên thực hiện

| MSSV | Họ và tên | Phần phụ trách |
|---|---|---|
| 24120323 | Huỳnh Thanh Huy | Logic Agent |
| 24120390 | Hồ Hữu Nghiêm | Validator và thực nghiệm |
| 24120379 | Chu Bảo Minh | Core Game, điều phối báo cáo và video demo |
| 24120304 | Trần Thị Bích Hạnh | DPLL SAT Solver |
| 24120427 | Võ Trúc Quỳnh | CNF Encoder |

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

### Chạy giao diện trên Ubuntu/WSL

Trên Ubuntu hoặc WSL có hỗ trợ ứng dụng đồ họa, mở terminal tại thư mục
gốc của repo. Nếu Python hệ thống báo `No module named 'tkinter'`,
cài Tkinter bằng lệnh sau:

```bash
sudo apt install python3-tk
```

Khởi chạy trò chơi bằng Python hệ thống:

```bash
cd Source
/usr/bin/python3 main.py
```

Để kiểm tra giao diện, chọn **3×3 Easy** rồi nhấn **BẮT ĐẦU**.
Bàn chơi sẽ hiện với thẻ **A1** đã mở.

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

Cả 9 màn đều có nghiệm duy nhất khi kiểm tra toàn bộ manh mối. Từ trạng thái công khai ban đầu, Logic Agent giải được cả 9 màn mà không cần đoán.

## 6. Kiểm thử và thực nghiệm

Các lệnh dưới đây chạy từ thư mục `Source`, trong môi trường Python đã cài
`requirements.txt` theo mục 2. Nếu đang ở thư mục gốc của repo, chạy `cd Source` trước.

### 6.1. Chạy kiểm thử

Chạy toàn bộ bộ test:

```bash
python -m unittest discover -s tests -v
```

Chạy riêng các test trong `test_logic_agent.py`:

```bash
python -m unittest tests.test_logic_agent -v
```

### 6.2. Chạy thực nghiệm trên Ubuntu/WSL

```bash
python -m experiments.run_experiments
```

Chương trình chạy 9 màn, mỗi màn 5 lượt, giới hạn 30 giây/lượt.
Cuối quá trình, terminal hiển thị số lượt hoàn tất, số lượt hết giờ và số lỗi.
Các file kết quả được cập nhật trong `experiments/results/`.

| File | Nội dung |
|---|---|
| `experiment_runs.csv` | Số liệu từng lượt chạy |
| `experiment_summary.csv` | Tổng hợp theo màn, gồm kết quả kiểm tra nghiệm duy nhất |
| `experiment_size_summary.csv` | Tổng hợp theo kích thước bàn 3×3, 4×4 và 5×5 |
| `experiment_results.json` | Kết quả thực nghiệm ở định dạng JSON |

### 6.3. Tạo bảng và biểu đồ

Sau khi chạy thực nghiệm, chạy tiếp:

```bash
python -m experiments.plot_results
```

Lệnh này đọc số liệu vừa ghi và tạo [bảng kết quả](Source/experiments/results/report_results_tables.md)
cùng 10 [biểu đồ PNG](Source/experiments/results/figures/).
Bảng ghi số biến chính/phụ, số mệnh đề CNF, số lần gọi SAT, decisions,
propagations, backtracks, số bước suy luận và thời gian giải.

Khi cập nhật báo cáo trên Ubuntu/WSL, chạy hai lệnh sau từ `Source`
(máy cần có `latexmk` và XeLaTeX):

```bash
cp experiments/results/figures/*.png ../report/figures/
(cd ../report && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex)
```

PDF sau khi biên dịch nằm tại [report/main.pdf](report/main.pdf).

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
│   ├── test_deduction.py
│   ├── test_dpll.py
│   ├── test_encoder.py
│   └── test_logic_agent.py
└── experiments/
    ├── run_experiments.py
    ├── plot_results.py
    └── results/
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
- `tests/`: Kiểm thử game, encoder, DPLL và Logic Agent.
- `experiments/`: Thực hiện các thí nghiệm đánh giá thuật toán.

## 8. Trạng thái và thông tin dự án

**Học phần:** CSC14003 - Cơ sở Trí tuệ Nhân tạo

**Tên đồ án:** Griductive Solver – Project 2

**Ngôn ngữ:** Python

**Giao diện:** Tkinter

**Thuật toán:** CNF Encoding, DPLL SAT Solver, Deductive Logic Agent

**Trạng thái hiện tại:**

- Game đã tích hợp CNF Encoder, DPLL SAT Solver, Logic Agent và Validator.
- Nhóm đã chạy thành công 48/48 unit test trên Ubuntu.
- Trong đợt thực nghiệm được trình bày ở chương 7, cả 9 màn đều có nghiệm duy nhất.
  Agent giải xong 45/45 lượt, không có lỗi hoặc lượt hết giờ.

Các thành viên cần giữ nguyên hợp đồng API trong `models.py` và bảo đảm Agent không truy cập thông tin ẩn của Game Engine.