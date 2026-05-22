import fitz
import numpy as np
from rapidocr_onnxruntime import RapidOCR
from collections import defaultdict

f = 'data/raw/MSR-2026_01.pdf'
ocr = RapidOCR()
page = fitz.open(f)[0]
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
result, _ = ocr(img)

lines = defaultdict(list)
for box, text, score in result:
    ys = [p[1] for p in box]
    xs = [p[0] for p in box]
    y = int(sum(ys) / len(ys) // 8)
    x = int(sum(xs) / len(xs))
    lines[y].append((x, text))

for key in sorted(lines.keys())[:260]:
    row = ' '.join([t for _, t in sorted(lines[key], key=lambda z: z[0])])
    if any(c.isalpha() for c in row):
        print(f"{key:03d}: {row}")
