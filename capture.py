import cv2
import time
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Callable
import contextlib
import os
import sys

# ============================================================================
# Low-level camera operations
# ============================================================================

def list_working_cameras(max_index=10) -> List[Tuple[int, int, int, float]]:
    """List all working cameras with their properties.
    
    Returns:
        List of tuples: (index, width, height, fps)
    """
    working = []
    # Suppress stderr during camera scanning to hide OpenCV warnings
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stderr(devnull):
            for i in range(max_index):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Windows: low-friction
                if cap.isOpened():
                    ok, _ = cap.read()
                    if ok:
                        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
                        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
                        fps = cap.get(cv2.CAP_PROP_FPS) or 0
                        working.append((i, w, h, fps))
                cap.release()
    return working

def open_camera(camera_idx: int) -> Optional[cv2.VideoCapture]:
    """Open a camera by index.
    
    Args:
        camera_idx: Camera index
        
    Returns:
        VideoCapture object if successful, None otherwise
    """
    cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        return None
    return cap

def read_frame(cap: cv2.VideoCapture) -> Tuple[bool, Optional[np.ndarray]]:
    """Read a frame from the camera.
    
    Args:
        cap: VideoCapture object
        
    Returns:
        Tuple of (success, frame)
    """
    return cap.read()

def get_camera_properties(cap: cv2.VideoCapture) -> Tuple[int, int, float]:
    """Get camera properties.
    
    Args:
        cap: VideoCapture object
        
    Returns:
        Tuple of (width, height, fps)
    """
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    if fps < 1:
        fps = 30.0
    return w, h, fps

# ============================================================================
# Display operations
# ============================================================================

def add_text_overlay(frame, text: str, position: Tuple[int, int] = (10, 30),
                     color: Tuple[int, int, int] = (0, 255, 0), 
                     font_scale: float = 1.0, thickness: int = 2):
    """Add text overlay to a frame.
    
    Args:
        frame: Image frame
        text: Text to display
        position: (x, y) position
        color: BGR color tuple
        font_scale: Font scale
        thickness: Font thickness
        
    Returns:
        Frame with text overlay
    """
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                font_scale, color, thickness)
    return frame

def display_frame(frame, window_name: str = "Live Camera View"):
    """Display a frame in a window.
    
    Args:
        frame: Image frame to display
        window_name: Name of the window
    """
    cv2.imshow(window_name, frame)

def wait_for_key(timeout: int = 1) -> Optional[int]:
    """Wait for a key press.
    
    Args:
        timeout: Timeout in milliseconds (0 = wait indefinitely, 1 = non-blocking)
        
    Returns:
        Key code if pressed, None otherwise
    """
    key = cv2.waitKey(timeout) & 0xFF
    return key if key != 255 else None

# ============================================================================
# High-level camera operations
# ============================================================================

def show_live_view(camera_idx: int, window_name: str = "Live Camera View",
                   overlay_text: Optional[str] = None,
                   key_handler: Optional[Callable[[int], str]] = None) -> str:
    """Display live view from the selected camera.
    
    Args:
        camera_idx: Camera index
        window_name: Window name
        overlay_text: Optional text to overlay on frame (default: "Camera {idx}")
        key_handler: Optional function to handle key presses. Should return:
                    'quit' to exit, 'next' to switch camera, or None to continue
            
    Returns:
        'quit' if user quit, 'next' if switching camera, 'select' if user selected, 'error' on error
    """
    cap = open_camera(camera_idx)
    if not cap:
        return 'error'
    
    if overlay_text is None:
        overlay_text = f"Camera {camera_idx}"
    
    while True:
        ok, frame = read_frame(cap)
        if not ok:
            cap.release()
            cv2.destroyWindow(window_name)
            return 'error'
        
        # Add overlay text
        frame = add_text_overlay(frame, overlay_text)
        
        # Display frame
        display_frame(frame, window_name)
        
        # Handle keyboard input
        key = wait_for_key(1)
        if key is not None:
            if key_handler:
                result = key_handler(key)
                if result in ('quit', 'next'):
                    cap.release()
                    cv2.destroyWindow(window_name)
                    return result
            else:
                # Default key handling
                if key == ord('q'):
                    cap.release()
                    cv2.destroyWindow(window_name)
                    return 'quit'
                elif key == ord('n'):
                    cap.release()
                    cv2.destroyWindow(window_name)
                    return 'next'
                elif key == ord('s'):
                    cap.release()
                    cv2.destroyWindow(window_name)
                    return 'select'
    
    cap.release()
    cv2.destroyWindow(window_name)
    return 'quit'

def record_video(camera_idx: int, duration: float = 2.0, 
                 output_path: Optional[Path] = None) -> Optional[Path]:
    """Record video from the selected camera.
    
    Args:
        camera_idx: Camera index
        duration: Recording duration in seconds
        output_path: Optional output path (default: Desktop/webcam_{idx}_{timestamp}.mp4)
        
    Returns:
        Path to saved video file, or None on error
    """
    cap = open_camera(camera_idx)
    if not cap:
        raise RuntimeError(f"Could not open camera index {camera_idx}")

    ok, frame = read_frame(cap)
    if not ok:
        cap.release()
        raise RuntimeError("Camera opened but couldn't read a frame.")

    w, h, fps = get_camera_properties(cap)

    if output_path is None:
        desktop = Path.home() / "Desktop"
        output_path = desktop / f"webcam_{camera_idx}_{int(time.time())}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Could not open VideoWriter. Try changing output to .avi with XVID.")

    t0 = time.time()
    while time.time() - t0 < duration:
        ok, frame = read_frame(cap)
        if not ok:
            break
        writer.write(frame)

    writer.release()
    cap.release()

    return output_path

# ============================================================================
# Interactive selection
# ============================================================================

def interactive_camera_selection(max_index: int = 10, 
                                 start_index: int = 0,
                                 verbose: bool = True) -> Optional[int]:
    """Interactive camera selection with live preview.
    
    Args:
        max_index: Maximum camera index to check
        start_index: Starting camera index
        verbose: Whether to print status messages
        
    Returns:
        Selected camera index, or None if user quit
    """
    cams = list_working_cameras(max_index=max_index)
    if not cams:
        if verbose:
            print("No working webcams found (tried indices 0..9). Close Zoom/Teams and retry.")
        return None

    if verbose:
        print("Detected webcams (by index):")
        for i, w, h, fps in cams:
            print(f"  index={i}  {w}x{h}  fps={fps:.1f}")

    available_indices = [i for i, _, _, _ in cams]
    
    if not available_indices:
        if verbose:
            print("No working cameras found.")
        return None
    
    # Find starting index in available cameras
    current_idx = 0
    if start_index in available_indices:
        current_idx = available_indices.index(start_index)
    
    if verbose:
        print("\n" + "="*50)
        print("Camera Selection Mode")
        print("="*50)
        print(f"Starting with camera {available_indices[current_idx]}")
        print("Controls:")
        print("  'q' - Quit")
        print("  'n' - Next camera")
        print("  's' - Select this camera")
        print("="*50)
    
    while True:
        if current_idx >= len(available_indices):
            current_idx = 0
        
        camera_idx = available_indices[current_idx]
        result = show_live_view(camera_idx)
        
        if result == 'next':
            current_idx += 1
            continue
        elif result == 'select':
            # User selected this camera
            cv2.destroyAllWindows()
            if verbose:
                print(f"\nCamera {camera_idx} selected!")
            return camera_idx
        else:
            # User pressed 'q' or error occurred
            break
    
    cv2.destroyAllWindows()
    
    if verbose:
        print("\nExiting...")
    
    return None  # User quit, no selection made

# ============================================================================
# Legacy main function (for backward compatibility)
# ============================================================================

def main():
    """Original main function for backward compatibility."""
    interactive_camera_selection()

if __name__ == "__main__":
    main()
