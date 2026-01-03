# logic/posture_score.py
def _safe_float(v):
    try:
        return float(v)
    except Exception:
        return None

class PostureScorer:
    def __init__(self):
        pass

    def score_posture(self, angles: dict, landmarks: dict):
        score = 0.0
        parts = 0
        out = {}

        # shoulders level
        if landmarks and 11 in landmarks and 12 in landmarks:
            sh_diff = abs(landmarks[11][1] - landmarks[12][1])
            out["shoulders_level"] = sh_diff < 30
            score += (1.0 if out["shoulders_level"] else 0.5)
            parts += 1
        else:
            out["shoulders_level"] = False

        # back straight
        back_left = angles.get("back_left")
        back_right = angles.get("back_right")
        if back_left:
            out["back_straight"] = back_left > 140
            score += (1.0 if out["back_straight"] else 0.5)
            parts += 1
        elif back_right:
            out["back_straight"] = back_right > 140
            score += (1.0 if out["back_straight"] else 0.5)
            parts += 1
        else:
            out["back_straight"] = False

        # hips aligned
        if landmarks and 23 in landmarks and 24 in landmarks:
            hips_diff = abs(landmarks[23][1] - landmarks[24][1])
            out["hips_aligned"] = hips_diff < 40
            score += (1.0 if out["hips_aligned"] else 0.5)
            parts += 1
        else:
            out["hips_aligned"] = False

        # knees stable
        kleft = angles.get("knee_left"); kright = angles.get("knee_right")
        if kleft or kright:
            kgood = False
            if kleft and 80 <= kleft <= 170:
                kgood = True
            if kright and 80 <= kright <= 170:
                kgood = True
            out["knees_stable"] = kgood
            score += (1.0 if kgood else 0.3)
            parts += 1
        else:
            out["knees_stable"] = False

        out["feet_good"] = False

        # forward lean check
        if landmarks and 0 in landmarks and (23 in landmarks or 24 in landmarks):
            nose_y = landmarks[0][1]
            hips_y = None
            if 23 in landmarks and 24 in landmarks:
                hips_y = (landmarks[23][1] + landmarks[24][1]) / 2
            elif 23 in landmarks:
                hips_y = landmarks[23][1]
            elif 24 in landmarks:
                hips_y = landmarks[24][1]
            if hips_y:
                out["lean_forward"] = (nose_y - hips_y) < -30
            else:
                out["lean_forward"] = False
        else:
            out["lean_forward"] = False

        out["spine_curve"] = False

        if parts > 0:
            percent = int(min(100, max(0, (score / parts) * 100)))
        else:
            percent = 80

        out["percent"] = percent
        out["score"] = percent
        return out
