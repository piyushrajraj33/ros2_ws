from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def read_root():
    return {"Fleet Manager": "Running"}

@app.post("/send_goal/")
def send_goal(x: float, y: float):
    cmd = f"ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \"{{header: {{frame_id: 'map'}}, pose: {{position: {{x: {x}, y: {y}, z: 0.0}}, orientation: {{w: 1.0}}}}}}\""
    subprocess.run(cmd, shell=True)
    return {"status": "Goal sent"}
