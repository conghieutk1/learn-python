#!/usr/bin/env python3
# mini_grep.py
# Final version: color highlight, include/exclude, max-bytes, multithread, follow -f, context A/B.
import argparse, re, sys, time, os, threading
from pathlib import Path
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- Printing with thread-safety ----------
_print_lock = threading.Lock()
def ts_print(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs)

# ---------- Color handling ----------
def should_color(mode: str) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    # auto
    return sys.stdout.isatty()

def make_highlighter(pat: re.Pattern, enable: bool):
    if not enable:
        # no-op: return original line
        return lambda line: line
    # red foreground ANSI
    RED, RESET = "\033[31m", "\033[0m"
    return lambda line: pat.sub(lambda m: f"{RED}{m.group(0)}{RESET}", line)

# ---------- Pattern compile ----------
def compile_pattern(pat: str, ignore_case: bool, fixed: bool) -> re.Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    if fixed:
        pat = re.escape(pat)
    try:
        return re.compile(pat, flags)
    except re.error as e:
        sys.exit(f"[ERROR] Regex lỗi: {e}")

# ---------- Extension filters ----------
def parse_ext_list(s: str | None):
    if not s:
        return None
    out = set()
    for e in s.split(","):
        e = e.strip().lower()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        out.add(e)
    return out or None

# ---------- Path iterator (files only) ----------
def iter_paths(targets, recursive: bool, inc_exts, exc_exts, max_bytes: int | None):
    for t in targets:
        if t == "-" or str(t) == "-":
            yield "-"
            continue
        p = Path(t)
        if p.is_file():
            if _filter_file(p, inc_exts, exc_exts, max_bytes):
                yield p
        elif p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            for x in it:
                if x.is_file() and _filter_file(x, inc_exts, exc_exts, max_bytes):
                    yield x
        else:
            ts_print(f"[WARN] Bỏ qua: {t} không phải file/folder", file=sys.stderr)

def _filter_file(p: Path, inc_exts, exc_exts, max_bytes: int | None) -> bool:
    sx = p.suffix.lower()
    if inc_exts and sx not in inc_exts:
        return False
    if exc_exts and sx in exc_exts:
        return False
    if max_bytes is not None:
        try:
            if p.stat().st_size > max_bytes:
                ts_print(f"[SKIP large] {p} ({p.stat().st_size} bytes)", file=sys.stderr)
                return False
        except OSError as e:
            ts_print(f"[ERROR] stat {p} thất bại: {e}", file=sys.stderr)
            return False
    return True

# ---------- Grep core (streaming) ----------
def grep_file_lines(lines_iter, pat: re.Pattern, before: int, after: int, show_name: str, highlight):
    before_buf = deque(maxlen=before)
    after_cnt = 0
    for raw in lines_iter:
        line = raw if isinstance(raw, str) else raw.decode(errors="replace")
        matched = pat.search(line) is not None
        if matched:
            # print before-context
            for ctx in before_buf:
                ts_print(f"{show_name}-", ctx.rstrip("\n"))
            before_buf.clear()
            ts_print(f"{show_name}:", highlight(line.rstrip("\n")))
            after_cnt = after
        elif after_cnt > 0:
            ts_print(f"{show_name}+", line.rstrip("\n"))
            after_cnt -= 1
        else:
            if before:
                before_buf.append(line)

def grep_path(path, pat: re.Pattern, before: int, after: int, encoding: str, highlight):
    if path == "-":  # stdin
        try:
            grep_file_lines(sys.stdin, pat, before, after, "<stdin>", highlight)
        except Exception as e:
            ts_print(f"[ERROR] đọc stdin thất bại: {e}", file=sys.stderr)
        return
    p = Path(path)
    try:
        with open(p, "r", encoding=encoding, errors="replace") as fh:
            grep_file_lines(fh, pat, before, after, str(p), highlight)
    except (OSError, UnicodeError) as e:
        ts_print(f"[ERROR] Mở {p} thất bại: {e}", file=sys.stderr)

def follow_file(p: Path, pat: re.Pattern, encoding: str, before: int, after: int, highlight):
    # tail -f đơn giản: nhảy cuối file và đọc phần append
    try:
        with open(p, "r", encoding=encoding, errors="replace") as fh:
            fh.seek(0, 2)
            before_buf = deque(maxlen=before)
            after_cnt = 0
            while True:
                pos = fh.tell()
                line = fh.readline()
                if not line:
                    time.sleep(0.2)
                    fh.seek(pos)
                    continue
                matched = pat.search(line) is not None
                if matched:
                    for ctx in before_buf:
                        ts_print(f"{p}-", ctx.rstrip("\n"))
                    before_buf.clear()
                    ts_print(f"{p}:", highlight(line.rstrip("\n")))
                    after_cnt = after
                elif after_cnt > 0:
                    ts_print(f"{p}+", line.rstrip("\n"))
                    after_cnt -= 1
                else:
                    if before:
                        before_buf.append(line)
    except (OSError, UnicodeError) as e:
        ts_print(f"[ERROR] follow {p} thất bại: {e}", file=sys.stderr)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(
        description="mini-grep: lọc log/file theo pattern (streaming, color, include/exclude, max-bytes, multithread)."
    )
    ap.add_argument("pattern", help="Regex hoặc chuỗi literal (dùng --fixed để literal).")
    ap.add_argument("paths", nargs="*", default=["-"],
                    help="File/thư mục để grep. '-' = stdin. Mặc định đọc stdin.")
    ap.add_argument("-R", "--recursive", action="store_true", help="Duyệt thư mục đệ quy.")
    ap.add_argument("-i", "--ignore-case", action="store_true", help="Không phân biệt hoa/thường.")
    ap.add_argument("-F", "--fixed", action="store_true", help="Tìm literal (re.escape).")
    ap.add_argument("-B", "--before", type=int, default=0, help="Số dòng context trước match.")
    ap.add_argument("-A", "--after", type=int, default=0, help="Số dòng context sau match.")
    ap.add_argument("-e", "--encoding", default="utf-8", help="Encoding khi đọc file (mặc định utf-8).")

    # New features
    ap.add_argument("--color", choices=["auto","always","never"], default="auto",
                    help="Highlight phần match. auto=terminal thì bật, piped thì tắt (mặc định).")
    ap.add_argument("--include", help="Chỉ grep file có đuôi này, ví dụ: .log,.txt (không phân biệt hoa/thường).")
    ap.add_argument("--exclude", help="Bỏ qua file có đuôi này, ví dụ: .sql,.json.")
    ap.add_argument("--max-bytes", type=int, help="Bỏ qua file lớn hơn N bytes (VD 104857600 cho 100MB).")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 1,
                    help="Số threads quét song song nhiều file (mặc định = số CPU).")
    ap.add_argument("-f", "--follow", action="store_true",
                    help="Tail -f 1 file (chỉ dùng khi paths là đúng 1 file, không dùng stdin/thư mục).")

    args = ap.parse_args()

    pat = compile_pattern(args.pattern, args.ignore_case, args.fixed)
    use_color = should_color(args.color)
    highlight = make_highlighter(pat, use_color)

    inc_exts = parse_ext_list(args.include)
    exc_exts = parse_ext_list(args.exclude)

    targets = list(iter_paths(args.paths, args.recursive, inc_exts, exc_exts, args.max_bytes))

    # follow mode: only one file, not stdin
    if args.follow:
        if len(targets) != 1 or targets[0] == "-":
            sys.exit("[ERROR] --follow chỉ dùng với đúng 1 file, không dùng stdin/thư mục.")
        follow_file(Path(targets[0]), pat, args.encoding, args.before, args.after, highlight)
        return

    # If only stdin, do single-thread
    if targets == ["-"]:
        grep_path("-", pat, args.before, args.after, args.encoding, highlight)
        return

    # Separate stdin if mixed (rare)
    if "-" in targets:
        grep_path("-", pat, args.before, args.after, args.encoding, highlight)
        targets = [t for t in targets if t != "-"]

    # Multithread scan for multiple files
    workers = max(1, int(args.threads))
    if workers == 1 or len(targets) <= 1:
        for p in targets:
            grep_path(p, pat, args.before, args.after, args.encoding, highlight)
    else:
        with ThreadPoolExecutor(max_workers=workers) as exe:
            futs = [exe.submit(grep_path, p, pat, args.before, args.after, args.encoding, highlight) for p in targets]
            for _ in as_completed(futs):
                pass  # output đã thread-safe qua ts_print

if __name__ == "__main__":
    main()
