#!/usr/bin/env python3
import random, time, argparse, string
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

LEVELS = ["INFO", "DEBUG", "WARNING", "ERROR"]
MESSAGES = [
    "User logged in",
    "Payment processed",
    "File not found",
    "Connection timeout",
    "Low memory warning",
    "Unauthorized access",
    "Task completed successfully",
    "Retrying connection",
    "Cache invalidated",
    "Service restarted",
]

def random_line(ts: float, error_rate: float) -> str:
    level = random.choices(LEVELS, weights=[70,15,10,5])[0]
    if random.random() < error_rate:
        level = "ERROR"
    msg = random.choice(MESSAGES)
    rand_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))} [{level}] {msg} (req={rand_id})\n"

def generate_file(path: Path, lines: int, error_rate: float):
    print(f"[+] Writing {path} ...")
    ts = time.time()
    with path.open("w") as f:
        for i in range(lines):
            f.write(random_line(ts + i, error_rate))
    print(f"    Done: {path.stat().st_size / 1024:.1f} KB")

def estimate_lines(mb: float, avg_line_len: int = 80):
    bytes_target = mb * 1024 * 1024
    return int(bytes_target / avg_line_len)

def main():
    ap = argparse.ArgumentParser(description="Generate large fake log files for testing mini grep")
    ap.add_argument("--dir", default="logs", help="output directory")
    ap.add_argument("--files", type=int, default=3, help="number of files")
    ap.add_argument("--mb", type=float, default=5, help="approx size per file (MB)")
    ap.add_argument("--error-rate", type=float, default=0.05, help="fraction of lines with ERROR")
    ap.add_argument("--threads", type=int, default=2, help="parallel file writers")
    args = ap.parse_args()

    Path(args.dir).mkdir(exist_ok=True)
    lines = estimate_lines(args.mb)
    print(f"[i] Generating ~{args.mb}MB x {args.files} files (~{lines:,} lines/file)...")

    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        for i in range(args.files):
            path = Path(args.dir) / f"app_{i+1}.log"
            ex.submit(generate_file, path, lines, args.error_rate)

if __name__ == "__main__":
    main()
