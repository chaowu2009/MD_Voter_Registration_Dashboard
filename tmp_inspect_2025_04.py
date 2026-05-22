from collections import defaultdict

import fitz
import numpy as np
from rapidocr_onnxruntime import RapidOCR

f = 'data/raw/MSR-2025_04.pdf'
ocr = RapidOCR()
page = fitz.open(f)[0]
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
result, _ = ocr(img)

lines = defaultdict(list)
for box, text, score in (result or []):
    ys = [p[1] for p in box]
    xs = [p[0] for p in box]
    y = int(sum(ys) / len(ys) // 8)
    x = int(sum(xs) / len(xs))
    lines[y].append((x, text))

rows = []
for key in sorted(lines.keys()):
    row = ' '.join([t for _, t in sorted(lines[key], key=lambda z: z[0])])
    rows.append((key, row))

for i, (k, row) in enumerate(rows):
    up = row.upper()
    if (' TOTAL ' in (' ' + up + ' ')) or up.startswith('TOTAL') or up.startswith('REP') or up.startswith('UNA') or up.startswith('UNA') or up.startswith('HIO') or up.startswith('UNAFF'):
        print(f"{i:03d} y{k:03d}: {row}")
        for j in range(i + 1, min(i + 4, len(rows))):
            print(f"    + {rows[j][1]}")
