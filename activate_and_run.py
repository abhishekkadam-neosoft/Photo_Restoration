#!/usr/bin/env python3
"""
Helper script to activate virtual environment and run photo restoration
"""

import os
import sys
import subprocess
import platform

def activate_venv():
    """Activate the virtual environment"""
    venv_name = "photo_restoration_env"
    
    if not os.path.exists(venv_name):
        print(f"Virtual environment '{venv_name}' not found!")
        print("Please run setup_environment.py first to create the environment.")
        return False
    
    # Determine the activation script path based on platform
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_name, "Scripts", "activate")
        python_path = os.path.join(venv_name, "Scripts", "python.exe")
    else:
        activate_script = os.path.join(venv_name, "bin", "activate")
        python_path = os.path.join(venv_name, "bin", "python")
    
    if not os.path.exists(python_path):
        print(f"Python not found in virtual environment: {python_path}")
        return False
    
    print(f"Virtual environment activated: {venv_name}")
    print(f"Python path: {python_path}")
    
    return python_path

def run_restoration_interactive():
    """Run the interactive photo restoration"""
    python_path = activate_venv()
    if not python_path:
        return False
    
    # Run the interactive restoration script
    cmd = [python_path, "run_restoration.py"]
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running restoration: {e}")
        return False

def run_test():
    """Run the test script"""
    python_path = activate_venv()
    if not python_path:
        return False
    
    # Run the test script
    cmd = [python_path, "test_setup.py"]
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running test: {e}")
        return False

def main():
    """Main function"""
    print("Photo Restoration - Environment Activator")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            return run_test()
        elif command == "run":
            return run_restoration_interactive()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: test, run")
            return False
    else:
        # Interactive mode
        print("Choose an option:")
        print("1. Test setup")
        print("2. Run photo restoration")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            return run_test()
        elif choice == "2":
            return run_restoration_interactive()
        elif choice == "3":
            print("Goodbye!")
            return True
        else:
            print("Invalid choice!")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 