"""
Main application that uses the capture module for camera operations.
"""
import os
import sys
# Suppress OpenCV warnings by redirecting stderr during imports
# The warnings are harmless and occur during camera scanning

import capture
import cv2
import time
from pathlib import Path
import image_processing
import socket
import struct


def main():
    """Main application entry point."""
    print("=" * 60)
    print("Camera Application")
    print("=" * 60)
    
    # Step 1: List available cameras
    print("\n[Step 1] Scanning for available cameras...")
    cameras = capture.list_working_cameras(max_index=10)
    
    if not cameras:
        print("❌ No working cameras found. Please check your camera connections.")
        return
    
    print(f"✓ Found {len(cameras)} working camera(s):")
    for idx, width, height, fps in cameras:
        print(f"  • Camera {idx}: {width}x{height} @ {fps:.1f} fps")
    
    # Step 2: Interactive camera preview and selection
    print("\n[Step 2] Starting camera preview and selection...")
    print("You will see a live preview of each camera.")
    print("Navigate with 'n' to preview different cameras, then press 's' to select.")
    
    selected_camera = capture.interactive_camera_selection(
        max_index=10,
        start_index=0,
        verbose=True
    )
    
    # Step 3: Handle selected camera
    if selected_camera is not None:
        print(f"\n[Step 3] ✓ Camera {selected_camera} has been selected!")
        print(f"\nYou can now use camera {selected_camera} for your application.")
        
        # Optional: Show confirmation preview
        response = input("\nWould you like to see a final preview of the selected camera? (y/n): ").strip().lower()
        if response == 'y':
            print("\nShowing final preview. Press 'q' to quit.")
            capture.show_live_view(selected_camera, overlay_text=f"Selected Camera {selected_camera}")
            cv2.destroyAllWindows()
            print("\nPreview closed.")
        
        # Step 4: Process camera stream with bright_or_dark
        print(f"\n[Step 4] Starting image processing...")
        print("Processing camera stream - calculating average intensity (brightness).")
        print("Press Ctrl+C to stop.\n")
        
        CRIO_IP = "192.164.1.2"
        PORT = 5010
        
        try:
            with socket.create_connection((CRIO_IP, PORT)) as s:
                # Process camera stream and print/send intensity every second
                intensity_generator = image_processing.bright_or_dark(selected_camera)
                last_print_time = time.time()
                
                for intensity in intensity_generator:
                    current_time = time.time()
                    
                    # Print and send every second
                    if current_time - last_print_time >= 1.0:
                        print(f"Average intensity: {intensity:.4f} (normalized 0-1)")
                        # Convert intensity (0-1 float) to bytes and send
                        # Convert numpy float64 to Python float, then pack as 4-byte float
                        intensity_float = float(intensity)
                        intensity_bytes = struct.pack('>f', intensity_float)
                        s.sendall(intensity_bytes)
                        last_print_time = current_time
                    
        except KeyboardInterrupt:
            print("\n\nProcessing stopped by user.")
        except Exception as e:
            print(f"\n❌ Error during processing: {e}")
        
        print(f"\nCamera {selected_camera} processing completed.")
    else:
        print("\n❌ No camera selected. Exiting.")


if __name__ == "__main__":
    main()

