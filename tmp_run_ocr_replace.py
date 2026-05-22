import traceback

print('before', flush=True)
try:
    import runpy
    runpy.run_path('tmp_ocr_replace.py')
    print('after', flush=True)
except Exception:
    traceback.print_exc()
    print('failed', flush=True)
