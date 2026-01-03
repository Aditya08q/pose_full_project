from typing import Dict, Tuple
import math


class ExerciseDetector:
    """
    Rule-based auto detection for ONLY:
    - squat
    - pushup
    - jumping_jack
    - russian_twist
    - deadlift
    """

    SUPPORTED = {
        "squat",
        "pushup",
        "jumping_jack",
        "russian_twist",
        "deadlift"
    }

    def __init__(self, gemini_client=None):
        self.gemini = gemini_client

    def predict(self, angles: Dict, landmarks: Dict) -> Tuple[str, float]:
        scores = {
            "squat": self._score_squat(angles),
            "pushup": self._score_pushup(angles),
            "jumping_jack": self._score_jumping_jack(angles),
            "russian_twist": self._score_russian_twist(angles),
            "deadlift": self._score_deadlift(angles),
        }

        # pick best
        ex, score = max(scores.items(), key=lambda x: x[1])

        if score < 0.4:
            return "unknown", 0.0

        return ex, min(1.0, score)

    # ------------------ SCORING FUNCTIONS ------------------

    def _score_squat(self, a):
        knee = a.get("knee_angle")
        hip = a.get("hip_angle")

        if knee is None or hip is None:
            return 0.0

        score = 0.0
        if knee < 100:
            score += 0.6
        if hip < 120:
            score += 0.4
        return score

    def _score_pushup(self, a):
        elbow = a.get("elbow_angle")
        shoulder = a.get("shoulder_angle")

        if elbow is None or shoulder is None:
            return 0.0

        score = 0.0
        if elbow < 110:
            score += 0.6
        if shoulder < 80:
            score += 0.4
        return score

    def _score_jumping_jack(self, a):
        shoulder = a.get("shoulder_angle")
        ankle = a.get("ankle_distance")

        if shoulder is None or ankle is None:
            return 0.0

        score = 0.0
        if shoulder > 140:
            score += 0.5
        if ankle > 1.2:
            score += 0.5
        return score

    def _score_russian_twist(self, a):
        torso = a.get("torso_rotation")

        if torso is None:
            return 0.0

        return 0.7 if abs(torso) > 25 else 0.0

    def _score_deadlift(self, a):
        hip = a.get("hip_angle")
        back = a.get("back_angle")

        if hip is None or back is None:
            return 0.0

        score = 0.0
        if hip < 100:
            score += 0.6
        if 150 < back < 180:
            score += 0.4
        return score
