#!/usr/bin/env python3
"""
Debug script for photo restoration - preserves output files
"""

import os
import tempfile
import shutil
from PIL import Image
import numpy as np
from photo_restoration_runner import restore_photos, make_grid

def debug_restoration_with_preserved_output():
    """Run restoration and preserve all output files"""
    
    print("🔍 Debug Photo Restoration with Preserved Output")
    print("=" * 50)
    
    # Create a permanent output directory
    debug_output_dir = "debug_output"
    if os.path.exists(debug_output_dir):
        shutil.rmtree(debug_output_dir)
    os.makedirs(debug_output_dir)
    
    print(f"📁 Output will be preserved in: {os.path.abspath(debug_output_dir)}")
    
    # Create test image with face-like features
    print("📸 Creating test image with face-like features...")
    test_image = create_face_like_image()
    
    # Create temporary input directory
    with tempfile.TemporaryDirectory() as temp_input_dir:
        input_path = os.path.join(temp_input_dir, "test_face.jpg")
        test_image.save(input_path)
        
        print(f"✅ Saved test image to: {input_path}")
        print(f"📁 Input directory contents: {os.listdir(temp_input_dir)}")
        
        # Run restoration
        print("🔄 Running photo restoration...")
        success = restore_photos(
            input_folder=temp_input_dir,
            output_folder=debug_output_dir,
            gpu_id=-1,  # Use CPU
            with_scratch=True,
            hr=False
        )
        
        print(f"✅ Restoration success: {success}")
        
        # Copy input image to debug output for reference
        shutil.copy2(input_path, os.path.join(debug_output_dir, "input_image.jpg"))
        
        # Analyze output structure
        analyze_output_structure(debug_output_dir)
        
        # Look for restored images
        find_restored_images(debug_output_dir, test_image)

def create_face_like_image():
    """Create an image that looks more like a face"""
    # Create a larger image (height, width, 3)
    img_array = np.random.randint(80, 180, (600, 800, 3), dtype=np.uint8)
    
    # Add face-like structure (simplified)
    # Head shape (oval)
    center_x, center_y = 400, 300
    for y in range(600):
        for x in range(800):
            # Create oval head shape
            dx = (x - center_x) / 200
            dy = (y - center_y) / 250
            if dx*dx + dy*dy < 1:
                # Face area
                img_array[y, x] = [180, 160, 140]  # Skin tone
            else:
                # Background
                img_array[y, x] = [100, 100, 100]
    
    # Add some "damage" - scratches and spots
    for i in range(30):
        x = np.random.randint(0, 800)
        y = np.random.randint(0, 600)
        # Add dark spots
        if y+2 <= 600 and x+2 <= 800:
            img_array[y:y+2, x:x+2] = [40, 40, 40]
    
    # Add some horizontal scratches
    for i in range(8):
        y = np.random.randint(0, 600)
        if y+1 <= 600:
            img_array[y:y+1, :] = [30, 30, 30]
    
    # Add sepia tone
    img_array = img_array.astype(np.float32)
    img_array[:, :, 0] = img_array[:, :, 0] * 0.393 + img_array[:, :, 1] * 0.769 + img_array[:, :, 2] * 0.189
    img_array[:, :, 1] = img_array[:, :, 0] * 0.349 + img_array[:, :, 1] * 0.686 + img_array[:, :, 2] * 0.168
    img_array[:, :, 2] = img_array[:, :, 0] * 0.272 + img_array[:, :, 1] * 0.534 + img_array[:, :, 2] * 0.131
    
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)

def analyze_output_structure(output_dir):
    """Analyze the complete output directory structure"""
    print(f"\n📁 Analyzing output structure in: {output_dir}")
    print("=" * 40)
    
    if not os.path.exists(output_dir):
        print("❌ Output directory does not exist!")
        return
    
    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth > max_depth:
            return
        
        if os.path.isdir(path):
            print(f"{prefix}📁 {os.path.basename(path)}/")
            try:
                items = os.listdir(path)
                for i, item in enumerate(sorted(items)):
                    item_path = os.path.join(path, item)
                    is_last = (i == len(items) - 1)
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    
                    if os.path.isdir(item_path):
                        print_tree(item_path, new_prefix, max_depth, current_depth + 1)
                    else:
                        size = os.path.getsize(item_path)
                        print(f"{new_prefix}📄 {item} ({size} bytes)")
            except PermissionError:
                print(f"{prefix}❌ Permission denied")
        else:
            size = os.path.getsize(path)
            print(f"{prefix}📄 {os.path.basename(path)} ({size} bytes)")
    
    print_tree(output_dir)

def find_restored_images(output_dir, original_image):
    """Find and display any restored images"""
    print(f"\n🔍 Searching for restored images in: {output_dir}")
    print("=" * 40)
    
    # Find all image files
    image_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir)
                size = os.path.getsize(full_path)
                image_files.append((rel_path, full_path, size))
    
    if not image_files:
        print("❌ No image files found in output directory!")
        print("This suggests the restoration process didn't produce any output images.")
        return
    
    print(f"✅ Found {len(image_files)} image file(s):")
    for rel_path, full_path, size in sorted(image_files):
        print(f"   📄 {rel_path} ({size} bytes)")
        
        # Try to open and display info
        try:
            img = Image.open(full_path)
            print(f"      Size: {img.size}, Mode: {img.mode}")
            
            # Save a copy to a more accessible location
            accessible_path = os.path.join("debug_output", f"found_{os.path.basename(rel_path)}")
            shutil.copy2(full_path, accessible_path)
            print(f"      Copied to: {accessible_path}")
            
        except Exception as e:
            print(f"      ❌ Error opening image: {e}")
    
    # Try to create comparison if we found restored images
    if len(image_files) > 1:
        print("\n🖼️ Creating comparison...")
        try:
            # Use the first found image as restored
            restored_path = image_files[0][1]
            restored_image = Image.open(restored_path)
            comparison = make_grid(original_image, restored_image)
            comparison.save(os.path.join(output_dir, "comparison.jpg"))
            print("✅ Comparison saved as: comparison.jpg")
        except Exception as e:
            print(f"❌ Error creating comparison: {e}")

def main():
    """Main function"""
    print("Debug Photo Restoration")
    print("=" * 30)
    
    # Check if photo_restoration directory exists
    if not os.path.exists("photo_restoration"):
        print("❌ photo_restoration directory not found!")
        print("Please run setup_environment.py first.")
        return
    
    debug_restoration_with_preserved_output()
    
    print(f"\n🎯 Debug complete! Check the 'debug_output' directory for results.")
    print(f"📁 Full path: {os.path.abspath('debug_output')}")

if __name__ == "__main__":
    main() 