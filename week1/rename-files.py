#!/usr/bin/env python3

# viết script rename 500 file theo pattern

# python rename-files.py week1/demo

import argparse, re, sys, csv
from pathlib import Path
from datetime import datetime

def parse_exts(exts):
    if not exts: return None
    out=set()
    for e in exts.split(","):
        e=e.strip()
        if not e: continue
        if not e.startswith("."): e="."+e
        out.add(e.lower())
    return out

def iter_files(root: Path, recursive: bool, exts):
    paths = root.rglob("*") if recursive else root.glob("*")
    for p in paths:
        if not p.is_file(): continue
        if exts and p.suffix.lower() not in exts: continue
        yield p

def sort_files(files, key):
    if key=="name":
        return sorted(files, key=lambda p: p.name.lower())
    if key=="mtime":
        return sorted(files, key=lambda p: p.stat().st_mtime)
    return list(files)

def build_new_name(p: Path, num, args):
    stem = p.stem
    ext  = p.suffix
    date = datetime.fromtimestamp(p.stat().st_mtime)

    # Mode A: regex find/replace on current name (stem+ext)
    if args.find is not None:
        base = p.name
        repl = args.repl if args.repl is not None else ""
        try:
            new_base = re.sub(args.find, repl, base)
        except re.error as e:
            raise SystemExit(f"[ERROR] Regex lỗi: {e}")
        return new_base

    # Mode B: template-based
    tpl = args.template or "{stem}{ext}"
    # hỗ trợ các placeholder phổ biến
    mapping = {
        "stem": stem,
        "ext": ext,
        "num": num,
        "prefix": args.prefix or "",
        "suffix": args.suffix or "",
        "date": date,  # dùng định dạng {date:%Y%m%d_%H%M%S}
    }
    try:
        new_base = tpl.format(**mapping)
    except Exception as e:
        raise SystemExit(f"[ERROR] Lỗi format template: {e}. "
                         f"Ví dụ: {{prefix}}{{num:03d}}_{{stem}}{{suffix}}{{ext}}")
    return new_base

def resolve_collision(target: Path):
    if not target.exists():
        return target
    parent = target.parent
    stem, ext = target.stem, target.suffix
    i = 1
    while True:
        cand = parent / f"{stem} ({i}){ext}"
        if not cand.exists(): return cand
        i += 1

def write_log(logfile: Path, pairs):
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with logfile.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["old_path","new_path","timestamp"])
        now = datetime.now().isoformat()
        for old, new in pairs:
            w.writerow([str(old), str(new), now])

def undo_from_log(logfile: Path, dry_run: bool):
    if not logfile.exists():
        print(f"[ERROR] Không tìm thấy log: {logfile}")
        return
    with logfile.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
    # hoàn tác theo thứ tự ngược lại
    for row in reversed(rows):
        newp = Path(row["new_path"])
        oldp = Path(row["old_path"])
        if not newp.exists():
            print(f"[WARN] Bỏ qua: {newp} không tồn tại.")
            continue
        if oldp.exists():
            # nếu tên cũ đã bị chiếm, thêm hậu tố
            target = resolve_collision(oldp)
        else:
            target = oldp
        print(("[UNDO-DRY] " if dry_run else "[UNDO] ") + f"{newp} -> {target.name}")
        if not dry_run:
            newp.rename(target)

def main():
    ap = argparse.ArgumentParser(
        description="Bulk rename files an toàn (dry-run mặc định)."
    )
    ap.add_argument("path", help="Thư mục chứa file")
    ap.add_argument("--recursive", action="store_true", help="Duyệt đệ quy")
    ap.add_argument("--ext", help="Lọc theo đuôi, ví dụ: jpg,png,txt")
    ap.add_argument("--sort", choices=["none","name","mtime"], default="name",
                    help="Thứ tự xử lý (ảnh hưởng đánh số).")
    ap.add_argument("--start", type=int, default=1, help="Số bắt đầu cho {num}")
    ap.add_argument("--step", type=int, default=1, help="Bước tăng số")
    ap.add_argument("--prefix", default="", help="Prefix khi dùng template")
    ap.add_argument("--suffix", default="", help="Suffix khi dùng template")

    mode = ap.add_mutually_exclusive_group(required=False)
    mode.add_argument("--find", help="Regex find (áp dụng lên toàn bộ tên file hiện tại)")
    ap.add_argument("--repl", default="", help="Chuỗi thay thế cho --find (mặc định rỗng)")
    mode.add_argument("--template",
                      help=("Template tên mới, ví dụ: "
                            "'{prefix}{num:03d}_{stem}{suffix}{ext}' "
                            "hoặc '{date:%Y%m%d}-{stem}{ext}'"))

    ap.add_argument("--apply", action="store_true", help="Thực thi (mặc định chỉ dry-run)")
    ap.add_argument("--log", default=".rename_log.csv", help="Đường dẫn file log để undo")
    ap.add_argument("--undo", action="store_true", help="Hoàn tác theo log")
    args = ap.parse_args()

    logfile = Path(args.log)

    if args.undo:
        undo_from_log(logfile, dry_run=not args.apply)
        return

    root = Path(args.path)
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"[ERROR] Thư mục không hợp lệ: {root}")

    exts = parse_exts(args.ext)
    files = list(iter_files(root, args.recursive, exts))
    files = sort_files(files, args.sort)

    if not files:
        print("[INFO] Không tìm thấy file phù hợp.")
        return

    pairs = []
    n = args.start
    for p in files:
        new_base = build_new_name(p, n, args)
        n += args.step
        target = p.with_name(new_base)
        if target.exists() and target.resolve() != p.resolve():
            target = resolve_collision(target)
        pairs.append((p, target))

    # In preview
    print("=== Preview (dry-run mặc định) ===")
    for old, new in pairs[:20]:
        print(f"{old.name} -> {new.name}")
    if len(pairs) > 20:
        print(f"... và {len(pairs)-20} file nữa")

    if args.apply:
        # Thực thi rename + ghi log cho khả năng undo
        for old, target in pairs:
            old.rename(target)
        write_log(logfile, pairs)
        print(f"[DONE] Đã rename {len(pairs)} file. Log: {logfile}")
    else:
        print("\n[DRY-RUN] Không có thay đổi. Thêm --apply để thực thi.")
        print(f"Có thể ghi log preview bằng: --apply (log tại {logfile})")

if __name__ == "__main__":
    main()