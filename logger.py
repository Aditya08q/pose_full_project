# logger.py
import csv
import time
import os
import pandas as pd

class CSVLogger:
    def __init__(self, out_dir="."):
        self.out_dir = out_dir
        ts = int(time.time())
        self.filename = f"session_{ts}.csv"
        self.filepath = os.path.join(out_dir, self.filename)

        self.records = []
        self.notes = []

        # Create CSV with header
        with open(self.filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "exercise",
                "summary",
                "posture_percent",
                "rep_count"
            ])

   
    # Logging main summary rows

    def log_summary(self, exercise, summary_text, posture_percent=None, rep_count=0):
        row = {
            "timestamp": int(time.time()),
            "exercise": exercise,
            "summary": summary_text,
            "posture_percent": posture_percent,
            "rep_count": rep_count
        }
        self.records.append(row)

        with open(self.filepath, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                row["timestamp"],
                row["exercise"],
                row["summary"],
                row["posture_percent"],
                row["rep_count"]
            ])

    # Gemini / AI notes
    def add_gemini_note(self, note_text):
        entry = {"timestamp": int(time.time()), "text": note_text}
        self.notes.append(entry)

    # Convert logs to DataFrame
  
    def get_dataframe(self):
        if not self.records:
            return pd.DataFrame(columns=["timestamp","exercise","summary","posture_percent","rep_count"])
        return pd.DataFrame(self.records)

    # CSV download support
 
    def get_csv_bytes(self):
        with open(self.filepath, "rb") as f:
            return f.read()

  
    #  session summary
  
    def get_aggregate(self):
        df = self.get_dataframe()
        if df.empty:
            return {"error": "No data recorded"}

        agg = {}
        for ex in df["exercise"].unique():
            sub = df[df["exercise"] == ex]
            agg[ex] = {
                "total_reps": int(sub["rep_count"].max()),
                "avg_posture": float(sub["posture_percent"].dropna().mean() if "posture_percent" in sub else 0),
                "entries": len(sub)
            }
        return agg

  
    # Export CSV + AI notes
    def export_session(self):
        # save notes
        notes_file = self.filename.replace(".csv", "_notes.txt")
        notes_path = os.path.join(self.out_dir, notes_file)

        with open(notes_path, "w") as f:
            for n in self.notes:
                f.write(f"{n['timestamp']} - {n['text']}\n")

        return self.filepath, notes_path
