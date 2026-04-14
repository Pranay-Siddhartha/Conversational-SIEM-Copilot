import sys
import os

# Add the root directory to sys.path so 'backend.*' imports work
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

from backend.main import app

# This is required for Vercel Python serverless functions
# The 'app' variable is now correctly imported from backend.main
