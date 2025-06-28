#!/usr/bin/env python3
"""
Test script to verify photo restoration is working correctly
"""

import os
import tempfile
import shutil
from PIL import Image
import numpy as np
from photo_restoration_runner import restore_photos, make_grid

def create_test_image():
    """Create a test image that looks more like an old photo"""
    # Create a more realistic test image
    img_array = np.random.randint(100, 200, (512, 512, 3), dtype=np.uint8)
    
    # Add some "old photo" characteristics
    # Add sepia tone
    img_array = img_array.astype(np.float32)
    img_array[:, :, 0] = img_array[:, :, 0] * 0.393 + img_array[:, :, 1] * 0.769 + img_array[:, :, 2] * 0.189
    img_array[:, :, 1] = img_array[:, :, 0] * 0.349 + img_array[:, :, 1] * 0.686 + img_array[:, :, 2] * 0.168
    img_array[:, :, 2] = img_array[:, :, 0] * 0.272 + img_array[:, :, 1] * 0.534 + img_array[:, :, 2] * 0.131
    
    # Add some "damage" - scratches and spots
    for i in range(20):
        x = np.random.randint(0, 512)
        y = np.random.randint(0, 512)
        # Add dark spots
        img_array[y:y+3, x:x+3] = [30, 30, 30]
    
    # Add some horizontal scratches
    for i in range(5):
        y = np.random.randint(0, 512)
        img_array[y:y+2, :] = [20, 20, 20]
    
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)

def check_model_files():
    """Check if required model files exist"""
    print("🔍 Checking model files...")
    
    required_files = [
        "photo_restoration/Face_Detection/shape_predictor_68_face_landmarks.dat",
        "photo_restoration/Face_Enhancement/checkpoints",
        "photo_restoration/Global/checkpoints"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                contents = os.listdir(file_path)
                print(f"✅ {file_path} (directory with {len(contents)} items)")
                if len(contents) == 0:
                    print(f"   ⚠️  Warning: Directory is empty!")
                    all_exist = False
            else:
                size = os.path.getsize(file_path)
                print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def test_photo_restoration():
    """Test the photo restoration process"""
    print("Testing Photo Restoration Process")
    print("=" * 40)
    
    # Check if photo_restoration directory exists
    if not os.path.exists("photo_restoration"):
        print("❌ photo_restoration directory not found!")
        print("Please run setup_environment.py first.")
        return False
    
    # Check if run.py exists
    if not os.path.exists("photo_restoration/run.py"):
        print("❌ run.py not found in photo_restoration directory!")
        print("Please run setup_environment.py first.")
        return False
    
    # Check model files
    if not check_model_files():
        print("❌ Some model files are missing or empty!")
        print("Please run setup_environment.py again to download all required files.")
        return False
    
    # Create test image
    print("📸 Creating test image...")
    test_image = create_test_image()
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save test image
        input_path = os.path.join(input_dir, "test_image.jpg")
        test_image.save(input_path)
        
        print(f"✅ Saved test image to: {input_path}")
        print(f"📁 Input directory contents: {os.listdir(input_dir)}")
        
        # Test restoration
        print("🔄 Testing photo restoration...")
        success = restore_photos(
            input_folder=input_dir,
            output_folder=output_dir,
            gpu_id=-1,  # Use CPU for testing
            with_scratch=True,
            hr=False  # Use standard resolution for faster testing
        )
        
        print(f"✅ Restoration success: {success}")
        
        if not success:
            print("❌ Restoration failed!")
            return False
        
        # Check output
        print(f"📁 Output directory contents: {os.listdir(output_dir) if os.path.exists(output_dir) else 'Output dir not found'}")
        
        # Check each stage directory
        stage_dirs = [
            "stage_1_restore_output",
            "stage_2_detection_output", 
            "stage_3_face_output",
            "final_output"
        ]
        
        for stage_dir in stage_dirs:
            stage_path = os.path.join(output_dir, stage_dir)
            if os.path.exists(stage_path):
                contents = os.listdir(stage_path)
                print(f"📁 {stage_dir}: {len(contents)} items")
                if contents:
                    print(f"   Contents: {contents}")
                    
                    # Check subdirectories
                    for item in contents:
                        item_path = os.path.join(stage_path, item)
                        if os.path.isdir(item_path):
                            sub_contents = os.listdir(item_path)
                            print(f"   📂 {item}/: {sub_contents}")
        
        # Look for results in various possible locations
        possible_output_dirs = [
            os.path.join(output_dir, "final_output"),
            output_dir,
            os.path.join(output_dir, "restored_image"),
            os.path.join(output_dir, "stage_1_restore_output", "restored_image"),
            os.path.join(output_dir, "stage_1_restore_output", "origin"),
            os.path.join(output_dir, "stage_3_face_output", "each_img")
        ]
        
        restored_image = None
        for output_subdir in possible_output_dirs:
            print(f"🔍 Checking: {output_subdir}")
            if os.path.exists(output_subdir):
                print(f"✅ Found: {output_subdir}")
                contents = os.listdir(output_subdir)
                print(f"📄 Contents: {contents}")
                
                # Look for restored image
                restored_path = os.path.join(output_subdir, "test_image.jpg")
                if os.path.exists(restored_path):
                    print(f"✅ Found restored image: {restored_path}")
                    restored_image = Image.open(restored_path)
                    break
                else:
                    # Check for any image files
                    for file in contents:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                            restored_path = os.path.join(output_subdir, file)
                            print(f"✅ Found image file: {restored_path}")
                            restored_image = Image.open(restored_path)
                            break
                    if restored_image:
                        break
        
        if restored_image:
            print("✅ Successfully found restored image!")
            print("🖼️ Creating comparison...")
            
            # Create comparison
            comparison = make_grid(test_image, restored_image)
            
            # Save results for inspection
            results_dir = "test_results"
            os.makedirs(results_dir, exist_ok=True)
            
            test_image.save(os.path.join(results_dir, "original.jpg"))
            restored_image.save(os.path.join(results_dir, "restored.jpg"))
            comparison.save(os.path.join(results_dir, "comparison.jpg"))
            
            print(f"✅ Test completed successfully!")
            print(f"📁 Results saved in: {results_dir}")
            print(f"   - original.jpg: Original test image")
            print(f"   - restored.jpg: Restored image")
            print(f"   - comparison.jpg: Before/after comparison")
            
            return True
        else:
            print("❌ No restored image found!")
            print("This might be because:")
            print("1. The test image doesn't contain faces (required for processing)")
            print("2. The model files are not properly loaded")
            print("3. The image format is not supported")
            return False

def main():
    """Main test function"""
    print("Photo Restoration Test")
    print("=" * 50)
    
    success = test_photo_restoration()
    
    if success:
        print("\n🎉 All tests passed! Photo restoration is working correctly.")
        print("You can now use the Gradio app or other scripts.")
    else:
        print("\n❌ Tests failed! Please check the setup and try again.")
        print("Make sure you've run setup_environment.py successfully.")

if __name__ == "__main__":
    main() 