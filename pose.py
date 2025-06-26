import mediapipe as mp # Pose detection
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence = 0.8, min_tracking_confidence = 0.8)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        continue
    # Converting to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    res = pose.process(img_rgb)
    
    annotated_img = img.copy()
    if res.pose_landmarks:
        mp_drawing.draw_landmarks(annotated_img, res.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color = (0, 255, 0), thickness = 2, circle_radius = 4), mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2))
    
    cv2.imshow('Pose Detection', annotated_img)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cap.destroyAllWindows()