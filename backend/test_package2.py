import sys
sys.path.insert(0, 'C:/Users/venka/Gen AI Hackathon/CrisisMesh/backend')

print("Testing import app...")
import app
print("app imported")

print("Testing import app.agents (before)...")
# Don't import agents yet
print("app.agents not imported yet")

print("Testing direct import app.agents.state...")
import app.agents.state
print("app.agents.state imported directly")

print("All imports successful!")