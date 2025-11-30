import sys
from pathlib import Path
# Ensure backend package is importable
backend_path = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_path))

import importlib
try:
    mod = importlib.import_module('app.main')
    app = mod.app
    print('Registered routes:')
    for r in app.routes:
        print(r.path)
except Exception as e:
    print('Error importing app.main:', e)
    import traceback
    traceback.print_exc()
