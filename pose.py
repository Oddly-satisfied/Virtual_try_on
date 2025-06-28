import cv2
import numpy as np
import mediapipe as mp
from scipy.interpolate import Rbf

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Load garment image with alpha transparency handling
garment_path = 'garment.png'
garment = cv2.imread(garment_path, cv2.IMREAD_UNCHANGED)

# Check if image has alpha channel
if garment is None:
    raise FileNotFoundError(f"Garment image not found at {garment_path}")

if garment.shape[2] == 4:  # Has alpha channel
    garment_rgb = garment[:, :, :3]
    garment_mask = garment[:, :, 3]
else:  # Create alpha channel
    garment_rgb = garment
    # Create opaque mask (fully visible)
    garment_mask = 255 * np.ones(garment.shape[:2], dtype=np.uint8)

# Combine into RGBA format
garment_rgba = cv2.merge([garment_rgb[:, :, 0], 
                          garment_rgb[:, :, 1], 
                          garment_rgb[:, :, 2], 
                          garment_mask])

# Define garment anchor points (normalized coordinates 0-1)
garment_points = np.array([
    [0.2, 0.1],  # Left shoulder
    [0.8, 0.1],  # Right shoulder
    [0.2, 0.7],  # Left hip
    [0.8, 0.7]   # Right hip
])

# Body landmark indices
LANDMARK_INDICES = {
    'LEFT_SHOULDER': mp_pose.PoseLandmark.LEFT_SHOULDER.value,
    'RIGHT_SHOULDER': mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
    'LEFT_HIP': mp_pose.PoseLandmark.LEFT_HIP.value,
    'RIGHT_HIP': mp_pose.PoseLandmark.RIGHT_HIP.value
}

def get_body_points(landmarks, frame_shape):
    """Convert normalized landmarks to pixel coordinates"""
    h, w = frame_shape[:2]
    return np.array([
        [landmarks[LANDMARK_INDICES['LEFT_SHOULDER']].x * w,
         landmarks[LANDMARK_INDICES['LEFT_SHOULDER']].y * h],
        [landmarks[LANDMARK_INDICES['RIGHT_SHOULDER']].x * w,
         landmarks[LANDMARK_INDICES['RIGHT_SHOULDER']].y * h],
        [landmarks[LANDMARK_INDICES['LEFT_HIP']].x * w,
         landmarks[LANDMARK_INDICES['LEFT_HIP']].y * h],
        [landmarks[LANDMARK_INDICES['RIGHT_HIP']].x * w,
         landmarks[LANDMARK_INDICES['RIGHT_HIP']].y * h]
    ])

def warp_garment(src_img, src_points, dst_points, output_shape):
    """Thin Plate Spline warping implementation"""
    # Create coordinate grids
    h, w = src_img.shape[:2]
    x = np.arange(w)
    y = np.arange(h)
    xx, yy = np.meshgrid(x, y)
    
    # Create interpolators
    rbf_x = Rbf(src_points[:,0], src_points[:,1], dst_points[:,0], function='thin_plate')
    rbf_y = Rbf(src_points[:,0], src_points[:,1], dst_points[:,1], function='thin_plate')
    
    # Generate new coordinates
    new_x = rbf_x(xx, yy)
    new_y = rbf_y(xx, yy)
    
    # Create output image
    warped = np.zeros((output_shape[0], output_shape[1], 4), dtype=np.uint8)
    
    # Map pixels (using vectorized operations for speed)
    valid_x = np.clip(new_x.astype(int), 0, output_shape[1]-1)
    valid_y = np.clip(new_y.astype(int), 0, output_shape[0]-1)
    
    # Use advanced indexing for assignment
    warped[valid_y, valid_x] = src_img[yy.astype(int), xx.astype(int)]
    
    return warped

# Initialize video capture
cap = cv2.VideoCapture(0)
user_height = 170  # Default height (cm)

# Get user height input
print("Enter your height in centimeters: ")
user_height = float(input().strip())

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue
    
    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process pose
    results = pose.process(rgb_frame)
    
    if results.pose_landmarks:
        # Draw pose landmarks
        mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(255,0,0), thickness=2)
        )
        
        # Get body points
        body_points = get_body_points(
            results.pose_landmarks.landmark,
            frame.shape
        )
        
        # Calculate garment size based on height
        shoulder_width_px = np.linalg.norm(body_points[0] - body_points[1])
        px_to_cm = user_height / (shoulder_width_px * 2.5)  # Anthropometric ratio
        
        # Scale garment points to body
        garment_pixel_points = garment_points * np.array([[garment_rgba.shape[1], garment_rgba.shape[0]]])
        warped_garment = warp_garment(
            garment_rgba,
            garment_pixel_points,
            body_points,
            frame.shape
        )
        
        # Blend garment with frame using alpha channel
        alpha = warped_garment[:, :, 3] / 255.0
        alpha = alpha[..., np.newaxis]  # Add channel dimension
        
        # Blend RGB channels
        frame = frame.astype(float)
        warped_rgb = warped_garment[:, :, :3].astype(float)
        blended = warped_rgb * alpha + frame * (1 - alpha)
        frame = blended.astype(np.uint8)
    
    # Display result
    cv2.imshow('Virtual Try-On', frame)
    
    # Exit on 'q'
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
