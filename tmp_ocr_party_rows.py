import fitz
import numpy as np
from rapidocr_onnxruntime import RapidOCR
from collections import defaultdict

for f in ['data/raw/MSR-2025_04.pdf', 'data/raw/MSR-2026_01.pdf']:
    print(f"\n=== {f} ===")
    ocr = RapidOCR()
    page = fitz.open(f)[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    result, _ = ocr(img)

    lines = defaultdict(list)
    for box, text, score in result:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        y = int(sum(ys) / len(ys) // 10)
        x = int(sum(xs) / len(xs))
        lines[y].append((x, text))

    keys = sorted(lines.keys())
    for key in keys:
        row = ' '.join([t for _, t in sorted(lines[key], key=lambda z: z[0])])
        up = row.upper()
        if any(tok in up for tok in ['TOTALACTIVE', 'TOTAL ACTIVE', 'REP ', ' UNA', 'UNA ', 'HIO', 'OTH', 'GRN', 'WCP', 'DEM', 'COUNTY', "GEORGE'S"]):
            print(f"{key:03d}: {row}")
