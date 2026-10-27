print("Starting import test...")
import sys
sys.path.insert(0, 'C:/Users/venka/Gen AI Hackathon/CrisisMesh/backend')

print("Importing app.config...")
from app.config import settings
print("Config loaded:", settings.APP_NAME)

print("Importing app.agents.state...")
import app.agents.state as state
print("State loaded")
print("AgentType:", state.AgentType.PLANNER)