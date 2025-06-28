#!/usr/bin/env python3
"""
Setup script for Bringing Old Photos Back to Life
This script will:
1. Create a virtual environment
2. Install all required dependencies
3. Clone the repository
4. Download all required model files
5. Set up the environment properly
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
import bz2
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def download_file(url, filename):
    """Download a file from URL"""
    print(f"Downloading {filename} from {url}")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False
    return True

def extract_zip(zip_path, extract_to):
    """Extract a zip file"""
    print(f"Extracting {zip_path} to {extract_to}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Successfully extracted {zip_path}")
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
        return False
    return True

def extract_bz2(bz2_path, extract_to):
    """Extract a bz2 file"""
    print(f"Extracting {bz2_path} to {extract_to}")
    try:
        with bz2.open(bz2_path, 'rb') as source, open(extract_to, 'wb') as target:
            shutil.copyfileobj(source, target)
        print(f"Successfully extracted {bz2_path}")
    except Exception as e:
        print(f"Error extracting {bz2_path}: {e}")
        return False
    return True

def check_package_installed(pip_path, package_name):
    """Check if a package is already installed"""
    try:
        result = subprocess.run([pip_path, "show", package_name], 
                              capture_output=True, text=True, check=False)
        return result.returncode == 0
    except:
        return False

def install_package_if_needed(pip_path, package_name, install_cmd=None):
    """Install a package only if it's not already installed"""
    if check_package_installed(pip_path, package_name):
        print(f"Package {package_name} already installed, skipping.")
        return True
    
    if install_cmd:
        print(f"Installing {package_name}...")
        return run_command(install_cmd, check=False)
    else:
        print(f"Installing {package_name}...")
        return run_command(f"{pip_path} install {package_name}", check=False)

def main():
    print("Setting up Bringing Old Photos Back to Life environment...")
    
    # Create virtual environment
    venv_name = "photo_restoration_env"
    if not os.path.exists(venv_name):
        print(f"Creating virtual environment: {venv_name}")
        run_command(f"python3 -m venv {venv_name}")
    else:
        print(f"Virtual environment {venv_name} already exists, skipping creation.")
    
    # Activate virtual environment and install requirements
    if sys.platform == "win32":
        activate_script = os.path.join(venv_name, "Scripts", "activate")
        pip_path = os.path.join(venv_name, "Scripts", "pip")
    else:
        activate_script = os.path.join(venv_name, "bin", "activate")
        pip_path = os.path.join(venv_name, "bin", "pip")
    
    print("Checking and installing base requirements...")
    run_command(f"{pip_path} install --upgrade pip")
    
    # Install packages only if not already installed
    install_package_if_needed(pip_path, "torch", f"{pip_path} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    install_package_if_needed(pip_path, "opencv-python", f"{pip_path} install opencv-python")
    install_package_if_needed(pip_path, "pillow", f"{pip_path} install pillow")
    install_package_if_needed(pip_path, "numpy", f"{pip_path} install numpy")
    install_package_if_needed(pip_path, "scipy", f"{pip_path} install scipy")
    install_package_if_needed(pip_path, "matplotlib", f"{pip_path} install matplotlib")
    install_package_if_needed(pip_path, "dlib", f"{pip_path} install dlib")
    install_package_if_needed(pip_path, "requests", f"{pip_path} install requests")
    install_package_if_needed(pip_path, "tqdm", f"{pip_path} install tqdm")
    install_package_if_needed(pip_path, "gradio", f"{pip_path} install gradio")
    
    # Clone the main repository
    if not os.path.exists("photo_restoration"):
        print("Cloning Bringing Old Photos Back to Life repository...")
        run_command("git clone https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life.git photo_restoration")
    else:
        print("Repository photo_restoration already exists, skipping clone.")
    
    # Change to the repository directory
    os.chdir("photo_restoration")
    
    # Install requirements from the repository
    if os.path.exists("requirements.txt"):
        print("Installing repository requirements...")
        run_command(f"../{pip_path} install -r requirements.txt")
    
    # Clone Synchronized-BatchNorm-PyTorch for Face Enhancement
    face_enhancement_networks = "Face_Enhancement/models/networks"
    sync_bn_face_path = os.path.join(face_enhancement_networks, "sync_batchnorm")
    if not os.path.exists(sync_bn_face_path):
        print("Setting up Synchronized-BatchNorm for Face Enhancement...")
        if not os.path.exists(face_enhancement_networks):
            os.makedirs(face_enhancement_networks, exist_ok=True)
        run_command("git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch", 
                   cwd=face_enhancement_networks)
        run_command("cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .", 
                   cwd=face_enhancement_networks)
    else:
        print("Synchronized-BatchNorm for Face Enhancement already exists, skipping setup.")
    
    # Clone Synchronized-BatchNorm-PyTorch for Global
    global_networks = "Global/detection_models"
    sync_bn_global_path = os.path.join(global_networks, "sync_batchnorm")
    if not os.path.exists(sync_bn_global_path):
        print("Setting up Synchronized-BatchNorm for Global...")
        if not os.path.exists(global_networks):
            os.makedirs(global_networks, exist_ok=True)
        run_command("git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch", 
                   cwd=global_networks)
        run_command("cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .", 
                   cwd=global_networks)
    else:
        print("Synchronized-BatchNorm for Global already exists, skipping setup.")
    
    # Download face landmark detection model
    face_detection_dir = "Face_Detection"
    landmark_file = os.path.join(face_detection_dir, "shape_predictor_68_face_landmarks.dat")
    if not os.path.exists(landmark_file):
        print("Downloading face landmark detection model...")
        if not os.path.exists(face_detection_dir):
            os.makedirs(face_detection_dir, exist_ok=True)
        bz2_file = os.path.join(face_detection_dir, "shape_predictor_68_face_landmarks.dat.bz2")
        if download_file("http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2", bz2_file):
            extract_bz2(bz2_file, landmark_file)
            os.remove(bz2_file)
    else:
        print("Face landmark detection model already exists, skipping download.")
    
    # Download face enhancement checkpoints
    face_enhancement_dir = "Face_Enhancement"
    face_checkpoints_dir = os.path.join(face_enhancement_dir, "checkpoints")
    face_checkpoints_zip = os.path.join(face_enhancement_dir, "face_checkpoints.zip")
    
    # Check if checkpoints directory exists and has content
    if not os.path.exists(face_checkpoints_dir) or not os.listdir(face_checkpoints_dir):
        print("Downloading face enhancement checkpoints...")
        if not os.path.exists(face_enhancement_dir):
            os.makedirs(face_enhancement_dir, exist_ok=True)
        if download_file("https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/face_checkpoints.zip", 
                         face_checkpoints_zip):
            extract_zip(face_checkpoints_zip, face_enhancement_dir)
            os.remove(face_checkpoints_zip)
    else:
        print("Face enhancement checkpoints already exist, skipping download.")
    
    # Download global checkpoints
    global_dir = "Global"
    global_checkpoints_dir = os.path.join(global_dir, "checkpoints")
    global_checkpoints_zip = os.path.join(global_dir, "global_checkpoints.zip")
    
    # Check if checkpoints directory exists and has content
    if not os.path.exists(global_checkpoints_dir) or not os.listdir(global_checkpoints_dir):
        print("Downloading global checkpoints...")
        if not os.path.exists(global_dir):
            os.makedirs(global_dir, exist_ok=True)
        if download_file("https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/global_checkpoints.zip", 
                         global_checkpoints_zip):
            extract_zip(global_checkpoints_zip, global_dir)
            os.remove(global_checkpoints_zip)
    else:
        print("Global checkpoints already exist, skipping download.")
    
    print("\nSetup completed successfully!")
    print(f"\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  {venv_name}\\Scripts\\activate")
    else:
        print(f"  source {venv_name}/bin/activate")
    print(f"\nTo run the photo restoration:")
    print(f"  python run.py --input_folder test_images/old --output_folder output --GPU -1")
    print(f"\nNote: Use --GPU -1 for CPU mode or --GPU 0 for GPU mode if you have CUDA")

if __name__ == "__main__":
    main() 