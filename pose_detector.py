import cv2
import mediapipe as mp
from utils.angles import calculate_angle

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_frame(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(img_rgb)

        annotated = frame.copy()
        landmarks = {}

        if res.pose_landmarks:
            h, w = frame.shape[:2]
            for i, lm in enumerate(res.pose_landmarks.landmark):
                landmarks[i] = (int(lm.x * w), int(lm.y * h))
            mp.solutions.drawing_utils.draw_landmarks(
                annotated,
                res.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        return annotated, {"landmarks": landmarks, "visibility": bool(landmarks)}

    def extract_angles(self, meta):
        lm = meta.get("landmarks", {}) or {}
        angles = {}

        try:
            # ---------- RAW JOINT ANGLES ----------
            if 23 in lm and 25 in lm and 27 in lm:
                angles["knee_left"] = calculate_angle(lm[23], lm[25], lm[27])
            if 24 in lm and 26 in lm and 28 in lm:
                angles["knee_right"] = calculate_angle(lm[24], lm[26], lm[28])

            if 11 in lm and 13 in lm and 15 in lm:
                angles["elbow_left"] = calculate_angle(lm[11], lm[13], lm[15])
            if 12 in lm and 14 in lm and 16 in lm:
                angles["elbow_right"] = calculate_angle(lm[12], lm[14], lm[16])

            if 11 in lm and 23 in lm and 25 in lm:
                angles["back_left"] = calculate_angle(lm[11], lm[23], lm[25])
            if 12 in lm and 24 in lm and 26 in lm:
                angles["back_right"] = calculate_angle(lm[12], lm[24], lm[26])

            if 11 in lm and 23 in lm and 27 in lm:
                angles["torso_left"] = calculate_angle(lm[11], lm[23], lm[27])
            if 12 in lm and 24 in lm and 28 in lm:
                angles["torso_right"] = calculate_angle(lm[12], lm[24], lm[28])

            # ---------- SEMANTIC ANGLES ----------
            if "knee_left" in angles and "knee_right" in angles:
                angles["knee_angle"] = (angles["knee_left"] + angles["knee_right"]) / 2

            if "elbow_left" in angles and "elbow_right" in angles:
                angles["elbow_angle"] = (angles["elbow_left"] + angles["elbow_right"]) / 2

            if "back_left" in angles and "back_right" in angles:
                angles["back_angle"] = (angles["back_left"] + angles["back_right"]) / 2

            if "torso_left" in angles and "torso_right" in angles:
                angles["torso_rotation"] = abs(
                    angles["torso_left"] - angles["torso_right"]
                )

            # Hip angle (shoulder–hip–knee)
            if 11 in lm and 23 in lm and 25 in lm and 12 in lm and 24 in lm and 26 in lm:
                left = calculate_angle(lm[11], lm[23], lm[25])
                right = calculate_angle(lm[12], lm[24], lm[26])
                angles["hip_angle"] = (left + right) / 2

            # Shoulder angle
            if 11 in lm and 13 in lm and 23 in lm and 12 in lm and 14 in lm and 24 in lm:
                left = calculate_angle(lm[13], lm[11], lm[23])
                right = calculate_angle(lm[14], lm[12], lm[24])
                angles["shoulder_angle"] = (left + right) / 2

            # Jumping jack feet distance
            if 27 in lm and 28 in lm:
                angles["ankle_distance"] = abs(lm[27][0] - lm[28][0]) / 300.0

        except Exception:
            pass

        return angles
