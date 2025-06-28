#!/usr/bin/env python3
"""
Simple script to run photo restoration on your own photos
"""

import os
import sys
from photo_restoration_runner import process_custom_photos

def main():
    print("Photo Restoration - Custom Photos")
    print("=" * 40)
    
    # Check if photo_restoration directory exists
    if not os.path.exists("photo_restoration"):
        print("Error: photo_restoration directory not found!")
        print("Please run setup_environment.py first to set up the environment.")
        return
    
    # Get input and output folders from user
    input_folder = input("Enter the path to your input photos folder: ").strip()
    output_folder = input("Enter the path for output results: ").strip()
    
    # Validate input folder
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist!")
        return
    
    # Ask for GPU preference
    gpu_choice = input("Use GPU? (y/n, default: n): ").strip().lower()
    gpu_id = 0 if gpu_choice == 'y' else -1
    
    # Ask for scratch removal
    scratch_choice = input("Use scratch removal? (y/n, default: y): ").strip().lower()
    with_scratch = scratch_choice != 'n'
    
    # Ask for high resolution
    hr_choice = input("Use high resolution mode? (y/n, default: y): ").strip().lower()
    hr = hr_choice != 'n'
    
    print(f"\nProcessing photos...")
    print(f"Input: {input_folder}")
    print(f"Output: {output_folder}")
    print(f"GPU: {'Yes' if gpu_id == 0 else 'No'}")
    print(f"Scratch removal: {'Yes' if with_scratch else 'No'}")
    print(f"High resolution: {'Yes' if hr else 'No'}")
    
    # Process the photos
    process_custom_photos(input_folder, output_folder, gpu_id, with_scratch, hr)

if __name__ == "__main__":
    main() 