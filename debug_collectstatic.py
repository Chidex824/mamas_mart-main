import os
import shutil
from pathlib import Path

src_root = Path(r'C:\Users\chide\OneDrive\Desktop\mamas_mart-main\mamas_mart-main\static')
out_root = Path(r'C:\Users\chide\OneDrive\Desktop\mamas_mart-main\mamas_mart-main\staticfiles')
out_root.mkdir(exist_ok=True)

count = 0
for src in sorted(src_root.rglob('*')):
    if src.is_file():
        rel = src.relative_to(src_root)
        dst = out_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        count += 1
        print(f'[{count}] {src} -> {dst}')
        try:
            shutil.copy2(str(src), str(dst))
            print('  OK')
        except Exception as e:
            print('  ERROR', type(e).__name__, e)
            print('  dst exists?', dst.exists())
            print('  dst parent exists?', dst.parent.exists())
            print('  dst name:', dst.name)
            print('  full path len:', len(str(dst)))
            raise

print('DONE', count)
