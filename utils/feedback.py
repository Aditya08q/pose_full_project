# utils/feedback.py
def generate_posture_summary(metrics):
    if not metrics:
        return "No posture data available."

    good = []
    bad = []
    tips = []

    if metrics.get("shoulders_level"):
        good.append("Shoulders are straight")
    if metrics.get("back_straight"):
        good.append("Back is upright")
    if metrics.get("hips_aligned"):
        good.append("Hips aligned properly")
    if metrics.get("knees_stable"):
        good.append("Knees stable")
    if metrics.get("feet_good"):
        good.append("Feet placement is correct")

    if metrics.get("lean_forward"):
        bad.append("Slight forward lean detected")
    if metrics.get("spine_curve"):
        bad.append("Spine could be straighter")
    if metrics.get("shoulder_uneven"):
        bad.append("Right shoulder is a little higher than the left")
    if metrics.get("knees_overbend"):
        bad.append("Avoid bending knees too much")

    good_text = "- No strong positives detected" if not good else "\n".join([f"- {g}" for g in good])
    bad_text = "- Looks good overall" if not bad else "\n".join([f"- {b}" for b in bad])

    tips = [
        "Pull shoulders slightly back",
        "Stand more upright",
        "Distribute weight evenly on both legs",
        "Keep your neck straight"
    ]

    score = metrics.get("score") or metrics.get("percent") or 80

    summary = " What You Did Well\n"
    summary += good_text + "\n\n"
    summary += " What Needs Improvement\n"
    summary += bad_text + "\n\n"
    summary += f"Estimated Posture Score\n{int(score)}% correct\n\n"
    summary += " Simple Correction Tips**\n"
    summary += "\n".join([f"- {t}" for t in tips]) + "\n\n"
    summary += " Exercise Note**\nYour rep is counted when your body returns to the starting position. Move slowly and with control."
    return summary
