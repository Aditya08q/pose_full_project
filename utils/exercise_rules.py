# utils/exercise_rules.py
from typing import Dict, Any, Optional
from utils.angles import calculate_angle
from math import inf


# Helpers
def _angle_from_landmarks(landmarks: Dict[int, tuple], a: int, b: int, c: int) -> Optional[float]:
    """Return angle ABC (B is vertex) in degrees, or None if any point missing."""
    try:
        if a in landmarks and b in landmarks and c in landmarks:
            return calculate_angle(landmarks[a], landmarks[b], landmarks[c])
    except Exception:
        pass
    return None

def _choose_first(*vals):
    """Return first non-None from vals or None."""
    for v in vals:
        if v is not None:
            return v
    return None

def _binary_threshold(angle: Optional[float], down_thresh: float, up_thresh: float) -> Dict[str, Any]:
    """Produce {primary_angle, down, up} with hysteresis thresholds."""
    if angle is None:
        return {"primary_angle": 0, "down": False, "up": False}
    return {"primary_angle": angle, "down": angle < down_thresh, "up": angle > up_thresh}


# Fitness exercises (15)
def squat(angles: Dict[str, float], landmarks: Dict[int, tuple]) -> Dict[str, Any]:
    # primary = knee angle (hip-knee-ankle). try left first then right
    a = _choose_first(
        _angle_from_landmarks(landmarks, 23, 25, 27),  # left hip-knee-ankle
        _angle_from_landmarks(landmarks, 24, 26, 28)   # right hip-knee-ankle
    )
    out = _binary_threshold(a, down_thresh=95, up_thresh=160)
    back = _choose_first(
        _angle_from_landmarks(landmarks, 11, 23, 25),
        _angle_from_landmarks(landmarks, 12, 24, 26)
    )
    out.update({"back_angle": back or 0, "back_ok": back is not None and back > 140})
    return out

def pushup(angles, landmarks):
    a = _choose_first(
        _angle_from_landmarks(landmarks, 12, 14, 16),  # right shoulder-elbow-wrist
        _angle_from_landmarks(landmarks, 11, 13, 15)   # left
    )
    out = _binary_threshold(a, down_thresh=65, up_thresh=160)
    hip_line = _choose_first(
        _angle_from_landmarks(landmarks, 11, 23, 25),
        _angle_from_landmarks(landmarks, 12, 24, 26)
    )
    out.update({"hip_line": hip_line or 0, "hip_ok": hip_line is not None and hip_line > 150})
    return out

def lunge(angles, landmarks):
    left = _angle_from_landmarks(landmarks, 23, 25, 27)
    right = _angle_from_landmarks(landmarks, 24, 26, 28)
    primary = _choose_first(left, right)
    out = _binary_threshold(primary, down_thresh=95, up_thresh=160)
    return out

def bicep_curl(angles, landmarks):
    a = _choose_first(
        _angle_from_landmarks(landmarks, 11, 13, 15),  # left shoulder-elbow-wrist
        _angle_from_landmarks(landmarks, 12, 14, 16)
    )
    # up = curl (angle small), down = extended
    if a is None:
        return {"primary_angle": 0, "up": False, "down": False}
    return {"primary_angle": a, "up": a < 50, "down": a > 150}

def shoulder_press(angles, landmarks):
    a = _choose_first(_angle_from_landmarks(landmarks, 11, 13, 15), _angle_from_landmarks(landmarks, 12, 14, 16))
    return _binary_threshold(a, down_thresh=80, up_thresh=165)

def tricep_dips(angles, landmarks):
    a = _choose_first(_angle_from_landmarks(landmarks, 11, 13, 15), _angle_from_landmarks(landmarks, 12, 14, 16))
    return _binary_threshold(a, down_thresh=70, up_thresh=150)

def deadlift(angles, landmarks):
    back = _choose_first(_angle_from_landmarks(landmarks, 11, 23, 27), _angle_from_landmarks(landmarks, 12, 24, 28))
    return {"primary_angle": back or 0, "back_ok": back is not None and back > 160}

def plank(angles, landmarks):
    bl = _choose_first(_angle_from_landmarks(landmarks, 11, 23, 27), _angle_from_landmarks(landmarks, 12, 24, 28))
    return {"primary_angle": bl or 0, "ok": bl is not None and bl > 165}

def jumping_jack(angles, landmarks):
    left_arm = _angle_from_landmarks(landmarks, 11, 13, 15)
    right_arm = _angle_from_landmarks(landmarks, 12, 14, 16)
    arms_up = (left_arm is not None and left_arm > 140) or (right_arm is not None and right_arm > 140)
    return {"primary_angle": _choose_first(left_arm, right_arm) or 0, "up": arms_up}

def high_knees(angles, landmarks):
    left = _angle_from_landmarks(landmarks, 23, 25, 27)
    right = _angle_from_landmarks(landmarks, 24, 26, 28)
    peak = max([v for v in (left, right) if v is not None] + [0])
    # "high" when knee angle indicates lift (smaller angle means knee closer to chest depending on camera)
    return {"primary_angle": peak, "high": peak < 100}

def side_leg_raise(angles, landmarks):
    left = _angle_from_landmarks(landmarks, 23, 25, 27)
    right = _angle_from_landmarks(landmarks, 24, 26, 28)
    angle = _choose_first(left, right)
    return {"primary_angle": angle or 0, "raised": angle is not None and angle < 150}

def mountain_climbers(angles, landmarks):
    left = _angle_from_landmarks(landmarks, 23, 25, 27)
    right = _angle_from_landmarks(landmarks, 24, 26, 28)
    val = min([v for v in (left, right) if v is not None] + [180])
    return {"primary_angle": val, "tuck": val < 90}

def glute_bridge(angles, landmarks):
    hip = _choose_first(_angle_from_landmarks(landmarks, 11, 23, 25), _angle_from_landmarks(landmarks, 12, 24, 26))
    return {"primary_angle": hip or 0, "up": hip is not None and hip > 150}

def wall_sit(angles, landmarks):
    left = _angle_from_landmarks(landmarks, 23, 25, 27)
    right = _angle_from_landmarks(landmarks, 24, 26, 28)
    avg = None
    if left and right:
        avg = (left + right) / 2
    elif left or right:
        avg = left or right
    return {"primary_angle": avg or 0, "ok": avg is not None and 80 <= avg <= 100}

def russian_twist(angles, landmarks):
    if 11 in landmarks and 12 in landmarks and 23 in landmarks and 24 in landmarks:
        shoulder_mid_x = (landmarks[11][0] + landmarks[12][0]) / 2
        hip_mid_x = (landmarks[23][0] + landmarks[24][0]) / 2
        diff = abs(shoulder_mid_x - hip_mid_x)
        return {"primary_angle": diff, "twist": diff > 25}
    return {"primary_angle": 0, "twist": False}


# Yoga / complex poses (10+)

def tree_pose(angles, landmarks):
    lh = landmarks.get(23, (0,0))
    rh = landmarks.get(24, (0,0))
    lk = landmarks.get(25, (0,0))
    rk = landmarks.get(26, (0,0))
    la = landmarks.get(27, (0,0))
    ra = landmarks.get(28, (0,0))

    support = 'right' if ra[1] > la[1] else 'left'
    if support == 'right':
        hip, knee, ankle = rh, rk, ra
    else:
        hip, knee, ankle = lh, lk, la

    leg_angle = calculate_angle(hip, knee, ankle)
    shoulders_mid_y = (landmarks.get(11,(0,0))[1] + landmarks.get(12,(0,0))[1]) / 2
    hips_mid_y = (lh[1] + rh[1]) / 2 if (lh and rh) else 0
    shoulders_level = abs(shoulders_mid_y - hips_mid_y) < 30
    return {"supporting_leg": support, "leg_angle": leg_angle, "balance": leg_angle > 165, "shoulders_level": shoulders_level}

def warrior_1(angles, landmarks):
    left_knee = _angle_from_landmarks(landmarks, 23, 25, 27)
    right_knee = _angle_from_landmarks(landmarks, 24, 26, 28)
    front = 'left' if left_knee is not None and (right_knee is None or abs(left_knee - 90) < abs(right_knee - 90)) else 'right'
    front_knee = left_knee if front == 'left' else right_knee
    return {"front": front, "front_knee": front_knee, "front_knee_ok": front_knee is not None and 80 <= front_knee <= 100}

def warrior_2(angles, landmarks):
    out = warrior_1(angles, landmarks)
    left_arm = _angle_from_landmarks(landmarks, 11, 13, 15)
    right_arm = _angle_from_landmarks(landmarks, 12, 14, 16)
    out.update({"left_arm": left_arm or 0, "right_arm": right_arm or 0, "arms_horizontal": left_arm is not None and right_arm is not None and left_arm > 150 and right_arm > 150})
    return out

def triangle_pose(angles, landmarks):
    shoulder = ((landmarks.get(11,(0,0))[0] + landmarks.get(12,(0,0))[0]) / 2, (landmarks.get(11,(0,0))[1] + landmarks.get(12,(0,0))[1]) / 2)
    hip = ((landmarks.get(23,(0,0))[0] + landmarks.get(24,(0,0))[0]) / 2, (landmarks.get(23,(0,0))[1] + landmarks.get(24,(0,0))[1]) / 2)
    ankle = ((landmarks.get(27,(0,0))[0] + landmarks.get(28,(0,0))[0]) / 2, (landmarks.get(27,(0,0))[1] + landmarks.get(28,(0,0))[1]) / 2)
    torso_angle = calculate_angle(shoulder, hip, ankle)
    return {"torso_side_angle": torso_angle, "ok_range": 25 <= torso_angle <= 35}

def cobra_pose(angles, landmarks):
    hip = landmarks.get(23, (0,0))
    shoulder = landmarks.get(11, (0,0))
    nose = landmarks.get(0, (0,0))
    back_angle = calculate_angle(hip, shoulder, nose)
    return {"back_extension_angle": back_angle, "extended": back_angle < 140}

def downward_dog(angles, landmarks):
    shoulder = ((landmarks.get(11,(0,0))[0] + landmarks.get(12,(0,0))[0]) / 2, (landmarks.get(11,(0,0))[1] + landmarks.get(12,(0,0))[1]) / 2)
    hip = ((landmarks.get(23,(0,0))[0] + landmarks.get(24,(0,0))[0]) / 2, (landmarks.get(23,(0,0))[1] + landmarks.get(24,(0,0))[1]) / 2)
    ankle = ((landmarks.get(27,(0,0))[0] + landmarks.get(28,(0,0))[0]) / 2, (landmarks.get(27,(0,0))[1] + landmarks.get(28,(0,0))[1]) / 2)
    angle = calculate_angle(shoulder, hip, ankle)
    return {"hip_angle": angle, "ok": 80 <= angle <= 100}

def chair_pose(angles, landmarks):
    left_knee = _angle_from_landmarks(landmarks, 23, 25, 27)
    right_knee = _angle_from_landmarks(landmarks, 24, 26, 28)
    knee_angle = (left_knee + right_knee) / 2 if left_knee and right_knee else left_knee or right_knee
    arms_up = _angle_from_landmarks(landmarks, 11, 13, 15)
    arms_ok = arms_up is not None and arms_up > 150
    return {"knee_angle": knee_angle or 0, "arms_up": arms_ok, "knee_ok": knee_angle is not None and 80 <= knee_angle <= 110}

def boat_pose(angles, landmarks):
    hip = ((landmarks.get(23,(0,0))[0] + landmarks.get(24,(0,0))[0]) / 2, (landmarks.get(23,(0,0))[1] + landmarks.get(24,(0,0))[1]) / 2)
    knee = ((landmarks.get(25,(0,0))[0] + landmarks.get(26,(0,0))[0]) / 2, (landmarks.get(25,(0,0))[1] + landmarks.get(26,(0,0))[1]) / 2)
    ankle = ((landmarks.get(27,(0,0))[0] + landmarks.get(28,(0,0))[0]) / 2, (landmarks.get(27,(0,0))[1] + landmarks.get(28,(0,0))[1]) / 2)
    hip_knee_ankle = calculate_angle(hip, knee, ankle)
    return {"hip_knee_ankle_angle": hip_knee_ankle, "ok": 90 <= hip_knee_ankle <= 110}

def bird_dog(angles, landmarks):
    left_arm = _angle_from_landmarks(landmarks, 11, 13, 15)
    right_leg = _angle_from_landmarks(landmarks, 24, 26, 28)
    return {"left_arm_angle": left_arm or 0, "right_leg_angle": right_leg or 0, "ok": left_arm is not None and right_leg is not None and left_arm > 150 and right_leg > 150}

def side_plank(angles, landmarks):
    shoulder = landmarks.get(11, (0,0))
    hip = landmarks.get(23, (0,0))
    ankle = landmarks.get(27, (0,0))
    line_angle = calculate_angle(shoulder, hip, ankle)
    return {"line_angle": line_angle or 0, "ok": 165 <= (line_angle or 0) <= 180}


# Compound / dynamic / Misc (remaining)

def burpees(angles, landmarks):
    # detect sequence presence via simple checks (not full state machine here)
    s = squat(angles, landmarks)
    p = plank(angles, landmarks)
    jj = jumping_jack(angles, landmarks)
    return {"squat": s, "plank": p, "jump": jj}

def surya_step_fold(angles, landmarks):
    torso = _angle_from_landmarks(landmarks, 11, 23, 27)
    return {"torso_angle": torso or 0, "folded": torso is not None and torso < 90}

def donkey_kicks(angles, landmarks):
    left = _angle_from_landmarks(landmarks, 23, 25, 27)
    right = _angle_from_landmarks(landmarks, 24, 26, 28)
    candidates = [v for v in (left, right) if v is not None]
    peak = max(candidates) if candidates else None
    return {"primary_angle": peak or 0, "kick": peak is not None and peak > 160}


# Fallback
def default_rule(angles, landmarks):
    return {"primary_angle": angles.get("primary_angle", 0) if angles else 0}

# Registry
RULES = {
    # fitness (15)
    "squat": squat,
    "pushup": pushup,
    "lunge": lunge,
    "bicep_curl": bicep_curl,
    "shoulder_press": shoulder_press,
    "tricep_dips": tricep_dips,
    "deadlift": deadlift,
    "plank": plank,
    "jumping_jack": jumping_jack,
    "high_knees": high_knees,
    "side_leg_raise": side_leg_raise,
    "mountain_climbers": mountain_climbers,
    "glute_bridge": glute_bridge,
    "wall_sit": wall_sit,
    "russian_twist": russian_twist,
    # yoga / complex (10+)
    "tree_pose": tree_pose,
    "warrior_1": warrior_1,
    "warrior_2": warrior_2,
    "triangle_pose": triangle_pose,
    "cobra_pose": cobra_pose,
    "downward_dog": downward_dog,
    "chair_pose": chair_pose,
    "boat_pose": boat_pose,
    "bird_dog": bird_dog,
    "side_plank": side_plank,
    # dynamic / compound
    "burpees": burpees,
    "surya_fold": surya_step_fold,
    "donkey_kicks": donkey_kicks
}

def get_rule(name: str):
    """Return rule function by name; fallback to default_rule."""
    return RULES.get(name, default_rule)
