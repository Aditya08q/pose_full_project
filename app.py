# app.py
import os
import time
import threading
import streamlit as st
import cv2
import numpy as np

from pose_detector import PoseDetector
from detector_ai import ExerciseDetector
from logic.counters import RepetitionCounter
from logic.posture_score import PostureScorer
from logger import CSVLogger
from gemini_client import GeminiClient
from utils.feedback import generate_posture_summary
from utils.exercise_rules import RULES

# streamlit-webrtc
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

st.set_page_config(page_title="Smart Pose Trainer", layout="wide")
st.title("Smart Pose Trainer  ")

# Sidebar (toggles)
st.sidebar.header("Settings")
INPUT_MODE = st.sidebar.selectbox("Input", ["Realtime Webcam", "Upload Video", "Upload Image"])
USE_GEMINI = st.sidebar.checkbox("Enable Gemini 2.5 ", value=False)
EXERCISE = st.sidebar.selectbox("Exercise", sorted(list(RULES.keys())))
SUMMARY_INTERVAL = st.sidebar.slider("Gemini summary ", 5, 30, 10)
DETECT_CONF = st.sidebar.slider("Detection confidence threshold", 0.0, 1.0, 0.5)

API_KEY = os.getenv("GOOGLE_API_KEY") if USE_GEMINI else None
gemini = GeminiClient(api_key=API_KEY) if (USE_GEMINI and API_KEY) else None

# core objects
pose_det = PoseDetector()
ai_det = ExerciseDetector(gemini_client=gemini)
counter = RepetitionCounter()
scorer = PostureScorer()
logger = CSVLogger(out_dir=".")
summary_buffer = []
summary_lock = threading.Lock()

def make_summary(exercise, angles, count_delta):
    return {"exercise": exercise, "timestamp": int(time.time()), "angles": angles, "count_delta": int(count_delta)}

def gemini_worker(interval_seconds):
    if not gemini:
        return
    while True:
        time.sleep(interval_seconds)
        with summary_lock:
            if not summary_buffer:
                continue
            batch = summary_buffer.copy()
            summary_buffer.clear()
        try:
            prompt = gemini.compose_prompt_from_summaries(batch)
            resp = gemini.predict(prompt, concise=True)
            logger.add_gemini_note(resp)
        except Exception as e:
            logger.add_gemini_note(f"Gemini error: {e}")

if USE_GEMINI and gemini:
    threading.Thread(target=gemini_worker, args=(SUMMARY_INTERVAL,), daemon=True).start()

# RTC config (public STUN)
RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

class Processor(VideoProcessorBase):
    def __init__(self):
        self.pose_det = pose_det
        self.ai = ai_det
        self.counter = counter
        self.scorer = scorer
        self.logger = logger
        self.gemini = gemini
        self.last_report_time = time.time()
        self.last_log_time = 0.0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        annotated, meta = self.pose_det.process_frame(img)
        landmarks = meta.get("landmarks", {})
        angles = self.pose_det.extract_angles(meta)

        # auto-detect exercise + confidence
        ex_name, conf = self.ai.predict(angles=angles, landmarks=landmarks)
        if conf < DETECT_CONF:
            ex_name = "unknown"

        # posture scoring & text summary
        posture = self.scorer.score_posture(angles, landmarks)
        summary_text = generate_posture_summary(posture)

        # store for UI
        st.session_state["current_summary"] = summary_text
        st.session_state["detected_exercise"] = ex_name
        st.session_state["detection_confidence"] = float(conf)

        # count using rule-based metrics when available
        metrics = RULES.get(ex_name, lambda a,l: {})(angles, landmarks) if ex_name in RULES else {}
        reps_before = self.counter.reps.get(ex_name, 0)
        curr_reps = self.counter.update(ex_name, metrics)
        reps_after = curr_reps

        # log summary when rep increments or periodically
        now_ts = time.time()
        should_log = False
        if reps_after > reps_before:
            should_log = True
        elif now_ts - self.last_log_time > max(2, SUMMARY_INTERVAL):
            should_log = True

        if should_log:
            self.logger.log_summary(ex_name, summary_text, posture.get("percent", None), rep_count=int(curr_reps))
            self.last_log_time = now_ts

        # overlay on frame
        cv2.putText(annotated, f"Exercise: {ex_name} ({conf:.2f})", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 180, 20), 2)
        cv2.putText(annotated, f"Reps: {int(curr_reps)}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 200, 20), 2)
        cv2.putText(annotated, f"Posture: {int(posture.get('percent',0))}%", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 20), 2)

        # batch to Gemini if available
        if self.gemini:
            delta = reps_after - reps_before
            send_ai = delta > 0 or (time.time() - self.last_report_time > SUMMARY_INTERVAL)
            if send_ai:
                with summary_lock:
                    summary_buffer.append(make_summary(ex_name, angles, int(delta)))
                self.last_report_time = time.time()

        return annotated

# UI layout
col1, col2 = st.columns([2,1])

with col1:
    st.header("Camera / Upload")
    if INPUT_MODE == "Realtime Webcam":
        st.write("Allow camera access and click Start.")
        webrtc_streamer(
            key="pose-rtc",
            rtc_configuration=RTC_CONFIGURATION,
            video_processor_factory=Processor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
            desired_playing_state=True
        )

    elif INPUT_MODE == "Upload Video":
        vid_file = st.file_uploader("Upload video", type=["mp4","mov","avi"])
        if vid_file:
            tmp = "tmp_uploaded.mp4"
            with open(tmp,"wb") as f:
                f.write(vid_file.read())
            cap = cv2.VideoCapture(tmp)
            stframe = st.empty()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                annotated, meta = pose_det.process_frame(frame)
                angles = pose_det.extract_angles(meta)
                ex_name, conf = ai_det.predict(angles=angles, landmarks=meta.get("landmarks", {}))
                if conf < DETECT_CONF:
                    ex_name = "unknown"
                metrics = RULES.get(ex_name, lambda a,l: {})(angles, meta.get("landmarks", {})) if ex_name in RULES else {}
                counter.update(ex_name, metrics)
                logger.log_summary(ex_name, generate_posture_summary(scorer.score_posture(angles, meta.get("landmarks", {}))),
                                   scorer.score_posture(angles, meta.get("landmarks", {})).get("percent", None),
                                   rep_count=counter.reps.get(ex_name,0))
                cv2.putText(annotated, f"Detected: {ex_name}", (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,180,20),2)
                stframe.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_column_width=True)
            cap.release()
            st.success("Video processed.")

    else:
        img_file = st.file_uploader("Upload image", type=["jpg","png","jpeg"])
        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            annotated, meta = pose_det.process_frame(frame)
            angles = pose_det.extract_angles(meta)
            ex_name, conf = ai_det.predict(angles=angles, landmarks=meta.get("landmarks", {}))
            posture = scorer.score_posture(angles, meta.get("landmarks", {}))
            st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_column_width=True)
            st.markdown(f"**Detected:** `{ex_name}` (conf {conf:.2f})")
            st.markdown("**Posture Summary**")
            st.markdown(generate_posture_summary(posture))

# show posture summary
if "current_summary" in st.session_state and st.session_state["current_summary"]:
    with col1:
        st.subheader("Posture Summary")
        st.markdown(st.session_state["current_summary"])

with col2:
    st.header("Session")
    st.write("Auto-detect: Enabled")
    st.write("Gemini:", "Enabled" if (USE_GEMINI and gemini) else "Disabled")
    st.write("Detection confidence threshold:", float(DETECT_CONF))
    st.write("Total summary rows logged:", len(logger.records))

    df = logger.get_dataframe()
    if df is not None:
        st.dataframe(df.tail(10))
        st.download_button("Download CSV", data=logger.get_csv_bytes(), file_name=logger.filename, mime="text/csv")

    if st.button("Generate final session report (Gemini)"):
        agg = logger.get_aggregate()
        if USE_GEMINI and gemini:
            try:
                report = gemini.generate_session_report(agg)
                logger.add_gemini_note(report)
                st.subheader("Gemini Session Report")
                st.text_area("Report", value=report, height=350)
            except Exception as e:
                st.error(f"Gemini error: {e}")
        else:
            st.subheader("Local Session Summary")
            st.json(agg)

    if st.button("Export session (CSV + notes)"):
        csv_path, notes_path = logger.export_session()
        st.success(f"Exported CSV -> {csv_path}, Notes -> {notes_path}")

# sidebar AI notes
if logger.notes:
    st.sidebar.header("AI Notes")
    for n in reversed(logger.notes[-5:]):
        st.sidebar.write(f"{n['timestamp']}: {n['text'][:200]}")
