# mini_grep.py — Hướng dẫn sử dụng

Tool nhỏ để tìm kiếm (grep) trong file/thư mục với các tính năng:
- Regex hoặc literal search
- Highlight màu (ANSI) cho phần match
- Include / exclude theo phần mở rộng
- Bỏ qua file lớn hơn N bytes
- Đa luồng (scan nhiều file song song)
- Tail -f cho 1 file
- Hiển thị context trước/sau (A/B)

Yêu cầu
- Python 3.7+
- Tốt nhất chạy trên terminal hỗ trợ ANSI (Windows: dùng Windows Terminal, PowerShell 7+ hoặc cmd với VT enabled)

Vị trí file
d:\Workspace\DevOps\Python\week2\mini_grep.py

Cách chạy (Windows)
```bash
cd "d:\Workspace\DevOps\Python\week2"
py -3 mini_grep.py "<pattern>" [paths...]
# Nếu không truyền paths thì mặc định đọc từ stdin ("-")
```

Tham số chính
- pattern: regex (mặc định) hoặc string khi dùng --fixed
- paths: file hoặc folder; '-' = stdin (mặc định)
- -R, --recursive: duyệt thư mục đệ quy
- -i, --ignore-case: không phân biệt hoa/thường
- -F, --fixed: treat pattern as literal (re.escape)
- -B, --before N: số dòng context trước match
- -A, --after N: số dòng context sau match
- -e, --encoding ENC: encoding khi đọc file (mặc định utf-8)
- --color {auto,always,never}: highlight (auto = bật khi terminal)
- --include: danh sách đuôi cần include, ví dụ ".log,.txt"
- --exclude: danh sách đuôi cần exclude
- --max-bytes N: bỏ qua file lớn hơn N bytes
- --threads N: số worker threads (mặc định = số CPU)
- -f, --follow: tail -f (chỉ dùng khi truyền đúng 1 file, không dùng stdin/thư mục)

Hành vi chính
- Màu chỉ bật khi --color=always hoặc terminal là TTY (auto).
- Khi đọc file gặp lỗi encoding sẽ dùng errors="replace".
- File lớn hơn --max-bytes được bỏ qua (với cảnh báo).
- Khi dùng stdin chỉ chạy trong single-thread.
- Output thread-safe bằng ts_print nên an toàn khi dùng --threads.

Ví dụ
- Tìm "ERROR" trong thư mục logs (đệ quy, hiển thị 2 dòng sau):
```bash
py -3 mini_grep.py "ERROR" "C:\logs" -R -A 2 --include ".log" --color auto
```
- Từ stdin:
```bash
type mylog.txt | py -3 mini_grep.py "timeout" -
```
- Tail -f:
```bash
py -3 mini_grep.py "ERROR" "C:\logs\app.log" -f
```
- Multithread, bỏ qua file >100MB:
```bash
py -3 mini_grep.py "Exception" "C:\logs" -R --threads 8 --max-bytes 104857600
```

Ghi chú
- Trên Windows, màu ANSI có thể cần terminal hỗ trợ; nếu thấy mã ANSI thay vì màu, thử --color=never hoặc dùng Windows Terminal.
- Tool tối ưu cho log/text files; không phù hợp để grep nhị phân.
- Mọi lỗi I/O sẽ in ra stderr và tool tiếp tục các file còn lại.

License
- Tự do sử dụng/tuỳ chỉnh (thêm license nếu cần).