"""
Entry point for Streamlit GUI.
Run with: streamlit run gui_app.py
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run the actual app
from src.view.gui.app import main

if __name__ == "__main__":
    main()
