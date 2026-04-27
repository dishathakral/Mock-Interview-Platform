import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    import config
    print("Successfully imported config")
    print("Supabase URL:", config.settings.supabase_url)
except ImportError as e:
    print(f"Failed to import config: {e}")
    print("sys.path:", sys.path)
except Exception as e:
    print(f"An error occurred: {e}")
