from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def list_agents() -> Dict[str, Any]:
    """List all available agents."""
    return {
        "agents": [
            "Safety Screener",
            "Nutritionist", 
            "Trainer",
            "Psychologist",
            "Accountability Buddy",
            "Progress Analyst",
            "Grocery Planner",
            "Schedule Optimizer",
            "Librarian"
        ]
    }

@router.post("/{agent_name}/execute")
async def execute_agent(agent_name: str) -> Dict[str, Any]:
    """Execute a specific agent."""
    # TODO: Implement agent execution logic
    return {"message": f"Agent {agent_name} execution - to be implemented"}
