import asyncio
import sys
sys.path.insert(0, 'C:/Users/venka/Gen AI Hackathon/CrisisMesh/backend')

from app.agents.graph import run_agent_pipeline
from app.agents.state import create_initial_state, SensorReading
from app.config import settings
from datetime import datetime

async def test_pipeline():
    print("Testing CrisisMesh agent pipeline...")
    print(f"SAMPLE_MODE: {settings.SAMPLE_MODE}")
    
    # Create sensor readings
    sensor_readings = [
        SensorReading(
            sensor_id="gauge_1",
            sensor_type="river_gauge",
            location=[-99.5, 30.0],
            timestamp=datetime.utcnow(),
            value=34.2,
            unit="ft",
            quality_flag="good"
        )
    ]
    
    # Create initial state
    state = create_initial_state(
        job_id="test-job-001",
        input_files=[],
        user_request="Respond to flash flood emergency in Guadalupe River area",
        user_preferences={},
        sensor_readings=sensor_readings,
        social_media_posts=[],
        official_alerts=[
            {
                "id": "nws_1",
                "type": "flash_flood_warning",
                "issued_at": "2025-07-04T01:14:00Z",
                "polygon": [[-99.7,30.1],[-99.2,30.1],[-99.2,29.9],[-99.7,29.9]],
                "severity": "critical"
            }
        ],
        disaster_context={
            "disaster_type": "flash_flood",
            "severity": "critical",
            "location": [-99.5, 30.0],
            "population_at_risk": 5000
        }
    )
    
    print(f"Initial state created: {state['job_id']}")
    
    # Run the pipeline
    result = await run_agent_pipeline(
        job_id="test-job-001",
        input_files=[],
        user_request="Respond to flash flood emergency in Guadalupe River area",
        user_preferences={},
        sensor_readings=sensor_readings,
        social_media_posts=[],
        official_alerts=[
            {
                "id": "nws_1",
                "type": "flash_flood_warning",
                "issued_at": "2025-07-04T01:14:00Z",
                "polygon": [[-99.7,30.1],[-99.2,30.1],[-99.2,29.9],[-99.7,29.9]],
                "severity": "critical"
            }
        ],
        disaster_context={
            "disaster_type": "flash_flood",
            "severity": "critical",
            "location": [-99.5, 30.0],
            "population_at_risk": 5000
        }
    )
    
    print(f"Final state: {result.get('status', 'unknown')}")
    print(f"Final output: {result.get('final_output', {})}")
    print(f"Errors: {result.get('errors', [])}")
    print(f"Trace length: {len(result.get('trace', []))}")
    
    if result.get('final_output'):
        print("\n✅ Pipeline executed successfully!")
        print(f"Disaster type: {result['final_output'].get('disaster_type')}")
        print(f"Evacuation ordered: {result['final_output'].get('evacuation_ordered')}")
        print(f"Alerts generated: {result['final_output'].get('alerts_generated')}")
        print(f"Assets dispatched: {result['final_output'].get('assets_dispatched')}")
        print(f"Shelters activated: {result['final_output'].get('shelters_activated')}")
    else:
        print("\n❌ Pipeline failed or no output")

if __name__ == "__main__":
    asyncio.run(test_pipeline())