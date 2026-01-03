Posture Pro — Full project
Files created under: /mnt/data/pose_full_project

Included:
- app.py : Streamlit app (webcam, image, video) with posture scoring, suggestions, exercise detection
- pose_utils.py : core pose processing + scoring + detection
- calibrate.py : helper to compute calibration JSON for Tree Pose
- clean_dataset.py : remove hidden/corrupted files from your dataset
- train_m1.py : optional training script (Apple Silicon optimized)
- requirements.txt : packages to install

Reference notebook (copied if available): /mnt/data/Fit_pose (1).ipynb
Reference example image (copied if available): /mnt/data/File64.jpg

Quick start:
1. Create and activate virtualenv:
   python3 -m venv posenv
   source posenv/bin/activate

2. Install requirements:
   pip install -r requirements.txt

3. (Optional) Clean dataset:
   python clean_dataset.py

4. (Optional) Calibrate Tree pose using your example image:
   python calibrate.py "/mnt/data/File64.jpg"

5. Run the app:
   streamlit run app.py
