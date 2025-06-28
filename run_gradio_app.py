#!/usr/bin/env python3
"""
Simple launcher for the Gradio Photo Restoration App
"""

import os
import sys
import subprocess
import platform

def activate_venv_and_run():
    """Activate virtual environment and run the Gradio app"""
    venv_name = "photo_restoration_env"
    
    if not os.path.exists(venv_name):
        print(f"Virtual environment '{venv_name}' not found!")
        print("Please run setup_environment.py first to create the environment.")
        return False
    
    # Determine the Python path based on platform
    if platform.system() == "Windows":
        python_path = os.path.join(venv_name, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_name, "bin", "python")
    
    if not os.path.exists(python_path):
        print(f"Python not found in virtual environment: {python_path}")
        return False
    
    print(f"Starting Gradio Photo Restoration App...")
    print(f"Virtual environment: {venv_name}")
    print(f"Python path: {python_path}")
    print(f"App will be available at: http://localhost:7860")
    print(f"Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the Gradio app
    try:
        cmd = [python_path, "gradio_app.py"]
        subprocess.run(cmd)
        return True
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        return True
    except Exception as e:
        print(f"Error running Gradio app: {e}")
        return False

def main():
    """Main function"""
    print("Photo Restoration - Gradio Web App Launcher")
    print("=" * 50)
    
    success = activate_venv_and_run()
    
    if not success:
        print("\nFailed to start the Gradio app.")
        print("Please make sure:")
        print("1. You've run setup_environment.py successfully")
        print("2. All dependencies are installed")
        print("3. The photo_restoration directory exists")
        sys.exit(1)

if __name__ == "__main__":
    main() 