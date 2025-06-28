#!/usr/bin/env python3
"""
Bringing Old Photos Back to Life - Standalone Runner
Converted from Colab notebook to work on local PC

This script provides functions to restore old photos using the Microsoft Bringing Old Photos Back to Life model.
"""

import os
import sys
import subprocess
import shutil
import io
import numpy as np
import PIL.Image
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {result.stderr}")
        return False
    return True

def make_grid(I1, I2, resize=True):
    """Create a side-by-side comparison grid of two images"""
    I1 = np.asarray(I1)
    H, W = I1.shape[0], I1.shape[1]

    if I1.ndim >= 3:
        I2 = np.asarray(I2.resize((W,H)))
        I_combine = np.zeros((H,W*2,3))
        I_combine[:,:W,:] = I1[:,:,:3]
        I_combine[:,W:,:] = I2[:,:,:3]
    else:
        I2 = np.asarray(I2.resize((W,H)).convert('L'))
        I_combine = np.zeros((H,W*2))
        I_combine[:,:W] = I1[:,:]
        I_combine[:,W:] = I2[:,:]
    I_combine = PIL.Image.fromarray(np.uint8(I_combine))

    W_base = 600
    if resize:
      ratio = W_base / (W*2)
      H_new = int(H * ratio)
      I_combine = I_combine.resize((W_base, H_new), PIL.Image.LANCZOS)

    return I_combine

def restore_photos(input_folder, output_folder, gpu_id=-1, with_scratch=False, hr=False):
    """
    Restore photos using the Bringing Old Photos Back to Life model
    
    Args:
        input_folder: Path to folder containing input images
        output_folder: Path to folder where restored images will be saved
        gpu_id: GPU ID to use (-1 for CPU, 0 for first GPU)
        with_scratch: Whether to use scratch removal mode
        hr: Whether to use high resolution mode
    """
    
    # Check if photo_restoration directory exists
    photo_restoration_dir = "photo_restoration"
    if not os.path.exists(photo_restoration_dir):
        print(f"Error: {photo_restoration_dir} directory not found.")
        print("Please run setup_environment.py first to set up the environment.")
        return False
    
    # Check if run.py exists in photo_restoration directory
    run_py_path = os.path.join(photo_restoration_dir, "run.py")
    if not os.path.exists(run_py_path):
        print(f"Error: run.py not found in {photo_restoration_dir} directory.")
        return False
    
    # Create output directory if it doesn't exist
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)
    
    # Build the command - run from photo_restoration directory
    cmd = f"python run.py --input_folder {input_folder} --output_folder {output_folder} --GPU {gpu_id}"
    
    if with_scratch:
        cmd += " --with_scratch"
    
    if hr:
        cmd += " --HR"
    
    print(f"Running photo restoration with command: {cmd}")
    print(f"Working directory: {photo_restoration_dir}")
    
    # Run the restoration from the photo_restoration directory
    success = run_command(cmd, cwd=photo_restoration_dir)
    
    if success:
        print(f"Photo restoration completed successfully!")
        print(f"Results saved to: {output_folder}")
    else:
        print("Photo restoration failed!")
    
    return success

def visualize_results(input_folder, output_folder):
    """Display before/after comparisons of restored photos"""
    input_path = Path(input_folder)
    output_path = Path(output_folder) / "final_output"
    
    if not output_path.exists():
        print(f"Output folder {output_path} does not exist!")
        return
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    filenames = [f for f in input_path.iterdir() 
                if f.is_file() and f.suffix.lower() in image_extensions]
    filenames.sort()
    
    print(f"Found {len(filenames)} images to process")
    
    for filename in filenames:
        print(f"Processing: {filename.name}")
        
        # Load original and restored images
        try:
            image_original = PIL.Image.open(filename)
            image_restore = PIL.Image.open(output_path / filename.name)
            
            # Create comparison grid
            comparison = make_grid(image_original, image_restore)
            
            # Save comparison
            comparison_path = output_path / f"comparison_{filename.name}"
            comparison.save(comparison_path)
            print(f"Comparison saved to: {comparison_path}")
            
        except Exception as e:
            print(f"Error processing {filename.name}: {e}")

def process_custom_photos(input_folder, output_folder, gpu_id=-1, with_scratch=True, hr=True):
    """
    Process custom photos uploaded by the user
    
    Args:
        input_folder: Path to folder containing user's photos
        output_folder: Path to folder where results will be saved
        gpu_id: GPU ID to use (-1 for CPU, 0 for first GPU)
        with_scratch: Whether to use scratch removal mode
        hr: Whether to use high resolution mode
    """
    
    # Create directories
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Processing photos from: {input_folder}")
    print(f"Results will be saved to: {output_folder}")
    
    # Run restoration
    success = restore_photos(input_folder, output_folder, gpu_id, with_scratch, hr)
    
    if success:
        # Visualize results
        visualize_results(input_folder, output_folder)
        
        print(f"\nAll processing completed!")
        print(f"Check the results in: {output_folder}")
    else:
        print("Processing failed!")

def main():
    """Main function to demonstrate usage"""
    print("Bringing Old Photos Back to Life - Standalone Runner")
    print("=" * 50)
    
    # Check if photo_restoration directory exists
    if not os.path.exists("photo_restoration"):
        print("Error: photo_restoration directory not found!")
        print("Please run setup_environment.py first to set up the environment.")
        return
    
    # Check if run.py exists
    if not os.path.exists("photo_restoration/run.py"):
        print("Error: run.py not found in photo_restoration directory!")
        print("Please run setup_environment.py first to set up the environment.")
        return
    
    # Example usage
    print("\nExample 1: Restore photos (normal mode)")
    print("-" * 40)
    
    # Check if test images exist
    test_input = "test_images/old"
    test_output = "output"
    
    if os.path.exists(test_input):
        print(f"Found test images in {test_input}")
        restore_photos(test_input, test_output, gpu_id=-1)  # Use CPU
        visualize_results(test_input, test_output)
    else:
        print(f"Test images not found in {test_input}")
        print("You can place your own images in a folder and specify the path.")
    
    print("\nExample 2: Restore photos with scratch removal")
    print("-" * 40)
    
    test_input_scratch = "test_images/old_w_scratch"
    if os.path.exists(test_input_scratch):
        print(f"Found test images with scratches in {test_input_scratch}")
        restore_photos(test_input_scratch, test_output, gpu_id=-1, with_scratch=True)
        visualize_results(test_input_scratch, test_output)
    else:
        print(f"Test images with scratches not found in {test_input_scratch}")
    
    print("\nTo process your own photos:")
    print("1. Create a folder with your old photos")
    print("2. Call: process_custom_photos('your_input_folder', 'your_output_folder')")
    print("3. Check the results in your_output_folder")

if __name__ == "__main__":
    main() 