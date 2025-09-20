"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

security = HTTPBasic()

# Load users from JSON file
def load_users():
    users_path = os.path.join(Path(__file__).parent, "users.json")
    with open(users_path, "r") as f:
        return json.load(f)

def authenticate(credentials: HTTPBasicCredentials):
    users = load_users()
    # Check teachers
    for teacher in users.get("teachers", []):
        if credentials.username == teacher["username"] and credentials.password == teacher["password"]:
            return {"role": "teacher", "username": credentials.username}
    # Check admins
    for admin in users.get("admins", []):
        if credentials.username == admin["username"] and credentials.password == admin["password"]:
            return {"role": "admin", "username": credentials.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities



# Only teachers/admins can sign up students
@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate(credentials)
    if user["role"] not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can sign up students.")
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity = activities[activity_name]
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}



# Only teachers/admins can unregister students
@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate(credentials)
    if user["role"] not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can unregister students.")
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity = activities[activity_name]
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
# Add a login endpoint for testing credentials
@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate(credentials)
    return {"message": f"Login successful for {user['role']} {user['username']}"}
