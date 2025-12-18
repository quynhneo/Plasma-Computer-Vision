"""
Image processing functions for camera streams.
"""
import cv2
import numpy as np
from typing import Optional, Generator
import capture


def bright_or_dark(camera_idx: int) -> Generator[float, None, None]:
    """Process camera stream and calculate average grayscale intensity.
    
    This function takes a camera stream, converts frames to grayscale,
    and yields the average intensity normalized to 0-1.
    
    Args:
        camera_idx: Camera index to process
        
    Yields:
        Average intensity value (0.0 to 1.0) for each frame processed
    """
    cap = capture.open_camera(camera_idx)
    if not cap:
        raise RuntimeError(f"Could not open camera index {camera_idx}")
    
    try:
        while True:
            ok, frame = capture.read_frame(cap)
            if not ok:
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate average intensity
            # Grayscale values are 0-255, so we normalize to 0-1
            avg_intensity = np.mean(gray) / 255.0
            
            yield avg_intensity
    finally:
        cap.release()


def bright_or_dark_single_frame(frame: np.ndarray) -> float:
    """Calculate average grayscale intensity for a single frame.
    
    Args:
        frame: Input frame (BGR format)
        
    Returns:
        Average intensity value (0.0 to 1.0)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate average intensity and normalize to 0-1
    avg_intensity = np.mean(gray) / 255.0
    
    return avg_intensity



