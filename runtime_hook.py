import os
import sys

def _append_run_path():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        print(f"Running in packaged mode. Base dir: {base_dir}")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Running in development mode. Base dir: {base_dir}")

    paths = [
        base_dir,
        os.path.join(base_dir, 'BASECLASS'),
        os.path.join(base_dir, 'COMM'),
        os.path.join(base_dir, 'gate_api'),
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"Adding path: {path}")
            if path not in sys.path:
                sys.path.insert(0, path)
        else:
            print(f"Warning: Path does not exist: {path}")

    print("Python path:", sys.path)
    print("Current working directory:", os.getcwd())
    print("Contents of base directory:", os.listdir(base_dir))

_append_run_path() 