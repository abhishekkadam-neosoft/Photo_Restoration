#!/usr/bin/env python3
"""
Test script to verify the photo restoration setup is working correctly
"""

import os
import sys
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import dlib
        print(f"✓ dlib imported successfully")
    except ImportError as e:
        print(f"✗ dlib import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"✓ PIL imported successfully")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        return False
    
    return True

def test_repository():
    """Test if the repository is properly set up"""
    print("\nTesting repository setup...")
    
    if not os.path.exists("photo_restoration"):
        print("✗ photo_restoration directory not found")
        return False
    
    if not os.path.exists("photo_restoration/run.py"):
        print("✗ run.py not found in photo_restoration directory")
        return False
    
    print("✓ Repository directory found")
    print("✓ run.py found")
    
    # Check for required model files
    required_files = [
        "photo_restoration/Face_Detection/shape_predictor_68_face_landmarks.dat",
        "photo_restoration/Face_Enhancement/checkpoints",
        "photo_restoration/Global/checkpoints"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} found")
        else:
            print(f"✗ {file_path} not found")
    
    return True

def test_sync_batchnorm():
    """Test if Synchronized-BatchNorm is properly set up"""
    print("\nTesting Synchronized-BatchNorm setup...")
    
    sync_bn_paths = [
        "photo_restoration/Face_Enhancement/models/networks/sync_batchnorm",
        "photo_restoration/Global/detection_models/sync_batchnorm"
    ]
    
    for path in sync_bn_paths:
        if os.path.exists(path):
            print(f"✓ {path} found")
        else:
            print(f"✗ {path} not found")
    
    return True

def create_test_image():
    """Create a simple test image for testing"""
    print("\nCreating test image...")
    
    try:
        import numpy as np
        from PIL import Image
        
        # Create a simple test image
        test_image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        test_image = Image.fromarray(test_image)
        
        # Create test directory
        test_dir = "test_images/old"
        os.makedirs(test_dir, exist_ok=True)
        
        # Save test image
        test_path = os.path.join(test_dir, "test_image.jpg")
        test_image.save(test_path)
        
        print(f"✓ Test image created: {test_path}")
        return test_path
        
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        return None

def test_photo_restoration():
    """Test if the photo restoration can run"""
    print("\nTesting photo restoration...")
    
    # Create test image
    test_image_path = create_test_image()
    if not test_image_path:
        return False
    
    # Try to run the restoration
    try:
        cmd = [
            "python", "run.py",
            "--input_folder", "../test_images/old",
            "--output_folder", "../test_output",
            "--GPU", "-1"  # Use CPU
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print(f"Working directory: photo_restoration")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd="photo_restoration")
        
        if result.returncode == 0:
            print("✓ Photo restoration test completed successfully")
            return True
        else:
            print(f"✗ Photo restoration test failed")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Photo restoration test timed out")
        return False
    except Exception as e:
        print(f"✗ Photo restoration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Photo Restoration Setup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check your virtual environment setup.")
        return False
    
    # Test repository
    if not test_repository():
        print("\n❌ Repository test failed. Please run setup_environment.py first.")
        return False
    
    # Test sync batchnorm
    if not test_sync_batchnorm():
        print("\n❌ Synchronized-BatchNorm test failed.")
        return False
    
    # Test photo restoration
    if not test_photo_restoration():
        print("\n❌ Photo restoration test failed.")
        return False
    
    print("\n✅ All tests passed! Your setup is working correctly.")
    print("\nYou can now use the photo restoration system:")
    print("1. Activate your virtual environment")
    print("2. Run: python run_restoration.py")
    print("3. Or use the functions in photo_restoration_runner.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 