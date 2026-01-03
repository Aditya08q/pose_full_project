# logic/counters.py
from collections import defaultdict

class RepetitionCounter:
    def __init__(self):
        self.state = defaultdict(lambda: "up")   # states: "up" or "down"
        self.reps = defaultdict(int)

    def update(self, ex_name: str, metrics: dict):
        st = self.state[ex_name]
        down_flag = bool(metrics.get("down")) or (metrics.get("primary_angle") is not None and metrics.get("primary_angle") < 95)
        up_flag = bool(metrics.get("up")) or (metrics.get("primary_angle") is not None and metrics.get("primary_angle") > 150)

        if st == "up" and down_flag:
            self.state[ex_name] = "down"
        elif st == "down" and up_flag:
            self.reps[ex_name] += 1
            self.state[ex_name] = "up"
        return self.reps[ex_name]

    def reset(self, ex_name=None):
        if ex_name:
            self.state[ex_name] = "up"
            self.reps[ex_name] = 0
        else:
            self.state = defaultdict(lambda: "up")
            self.reps = defaultdict(int)
