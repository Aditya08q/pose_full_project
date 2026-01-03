# utils/angles.py
import math

def calculate_angle(a, b, c):
    """
    Angle at b formed by points a-b-c. Points are (x,y) or None.
    Returns angle in degrees (float). Safe on bad inputs.
    """
    if a is None or b is None or c is None:
        return 0.0
    try:
        ax, ay = float(a[0]), float(a[1])
        bx, by = float(b[0]), float(b[1])
        cx, cy = float(c[0]), float(c[1])
    except Exception:
        return 0.0
    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)
    dot = ba[0]*bc[0] + ba[1]*bc[1]
    mag = (math.hypot(ba[0], ba[1]) * math.hypot(bc[0], bc[1])) + 1e-7
    cosv = max(min(dot / mag, 1.0), -1.0)
    return float(math.degrees(math.acos(cosv)))
