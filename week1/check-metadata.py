from pathlib import Path
from datetime import datetime
import stat

p = Path("./rename-files.py")
print(dir(p))
print(p.stat())
print(f"File exists: {p.exists()}")
print(f"Is file: {p.is_file()}")
mtime = p.stat().st_mtime
ctime = p.stat().st_ctime

print(f"File: {p.name}")
print(f"Size: {p.stat().st_size} bytes")
print(f"Creation time: {datetime.fromtimestamp(ctime)}")
print(f"Last modified: {datetime.fromtimestamp(mtime)}")
print(f"File: {p.stat().st_mode}")
print(stat.filemode(p.stat().st_mode))
st_uid = p.stat().st_uid
st_gid = p.stat().st_gid
print(f"UID: {st_uid}, GID: {st_gid}")
