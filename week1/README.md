# rename-files.py — Hướng dẫn sử dụng

Script tiện ích để đổi tên hàng loạt file an toàn (mặc định dry-run). Hỗ trợ: lọc theo đuôi, duyệt đệ quy, sắp xếp, template tên mới, hoặc dùng regex find/replace. Ghi log để hoàn tác.

## Yêu cầu
- Python 3.6+
- Chạy trên Windows (hướng dẫn lệnh phù hợp)

## Vị trí file
d:\Workspace\DevOps\Python\week1\rename-files.py

## Cách chạy
Mở terminal (Ctrl+`) và chuyển đến thư mục chứa script:
```bash
cd "d:\Workspace\DevOps\Python\week1"
py -3 rename-files.py "C:\đường\đến\thư_mục"
```

Mặc định script chỉ hiển thị preview (dry-run). Thêm `--apply` để thực hiện đổi tên.

## Các tham số chính
- path (positional) : thư mục chứa file (bắt buộc)
- --recursive : duyệt đệ quy
- --ext jpg,png,txt : lọc theo đuôi (không phân biệt hoa/thường)
- --sort {none,name,mtime} : thứ tự xử lý (mặc định `name`)
- --start N, --step N : số bắt đầu và bước tăng cho placeholder `{num}`
- --prefix, --suffix : chuỗi thêm vào khi dùng template
- --find REGEX : chế độ regex find (áp dụng lên tên file hiện tại)
- --repl STR : chuỗi thay thế cho `--find` (mặc định rỗng)
- --template TPL : template tên mới, ví dụ:
  - `{prefix}{num:03d}_{stem}{suffix}{ext}`
  - `{date:%Y%m%d}-{stem}{ext}`
  Placeholder có sẵn: `stem`, `ext`, `num`, `prefix`, `suffix`, `date`
- --apply : thực thi (mặc định chỉ preview)
- --log PATH : đường dẫn file log (mặc định `.rename_log.csv`)
- --undo : hoàn tác theo log (xem lưu ý)

## Ví dụ

1) Preview đổi tên theo template (không thay đổi file)
```bash
py -3 rename-files.py "C:\Photos" --ext jpg,png --template "{prefix}{num:04d}_{stem}{ext}" --prefix "IMG_"
```

2) Thực thi đổi tên
```bash
py -3 rename-files.py "C:\Photos" --ext jpg,png --template "{prefix}{num:04d}_{stem}{ext}" --prefix "IMG_" --apply
```

3) Dùng regex để xóa tiền tố `IMG_` (preview)
```bash
py -3 rename-files.py "C:\Photos" --find "^IMG_" --repl ""
```

4) Hoàn tác theo log
- Dry-run undo:
```bash
py -3 rename-files.py . --log ".rename_log.csv" --undo
```
- Thực hiện undo:
```bash
py -3 rename-files.py . --log ".rename_log.csv" --undo --apply
```

## Lưu ý an toàn
- Mặc định là dry-run: luôn kiểm tra preview trước khi thêm `--apply`.
- Preview chỉ hiển thị 20 file đầu tiên, phần còn lại sẽ hiển thị tổng số.
- Khi trùng tên đích, script tự thêm hậu tố " (i)" để tránh ghi đè.
- Log file CSV chứa cột: `old_path`, `new_path`, `timestamp`. Dùng log để undo.
- Khi dùng `--find` viết regex đúng cú pháp; lỗi regex sẽ dừng script với thông báo.

## Ghi chú kỹ thuật ngắn
- Template hỗ trợ định dạng ngày: `{date:%Y%m%d_%H%M%S}` hoặc các định dạng datetime chuẩn.
- Nếu template format sai, script sẽ hiển thị lỗi và ví dụ mẫu.
- Undo chạy các bước trong thứ tự ngược lại (đảm bảo khôi phục chính xác).

Nếu cần, cung cấp ví dụ thư mục cụ thể hoặc yêu cầu tinh chỉnh script (ví dụ: tắt resolve-collision, thay đổi định dạng log) để tôi hướng dẫn chi tiết.