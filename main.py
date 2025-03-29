from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import json
import asyncio
from agents import LearningAgents
from crewai import Crew, Process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class Resource(BaseModel):
    title: str
    description: Optional[str] = ""
    link: Optional[str] = ""
    rating: Optional[str] = ""
    justification: Optional[str] = ""

class RecommendationsResponse(BaseModel):
    recommendations: List[Resource]

class UserInput(BaseModel):
    user_input: str

# Initialize FastAPI app
app = FastAPI(title="Learning Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize learning agents
learning_agents = LearningAgents()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

@app.post("/recommendations/", response_model=RecommendationsResponse)
async def get_learning_recommendations(data: UserInput):
    try:
        logger.info(f"Received request with input: {data.user_input}")
        
        if not data.user_input.strip():
            raise HTTPException(status_code=400, detail="User input cannot be empty")

        # Define tasks
        interest_analysis_task = learning_agents.define_interest_analysis_task(data.user_input)
        resource_search_task = learning_agents.define_resource_search_task("user interests summary")
        resource_evaluation_task = learning_agents.define_resource_evaluation_task("list of resources")
        recommendation_task = learning_agents.define_recommendation_task("evaluated resources")

        # Create and run crew
        learning_crew = Crew(
            agents=[
                learning_agents.interest_analyzer_agent(),
                learning_agents.resource_searcher_agent(),
                learning_agents.resource_evaluator_agent(),
                learning_agents.recommendation_agent()
            ],
            tasks=[
                interest_analysis_task,
                resource_search_task,
                resource_evaluation_task,
                recommendation_task
            ],
            process=Process.sequential,
            verbose=True
        )

        try:
            # Remove await since kickoff() is not a coroutine
            result = learning_crew.kickoff()
            logger.info(f"Crew result: {result}")
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")

        
        # Process recommendations
        recommendations_output = None
        for task in learning_crew.tasks:
            if task.description.startswith("Create JSON array"):
                recommendations_output = task.output.result if hasattr(task.output, 'result') else str(task.output)
                break

        if not recommendations_output:
            raise HTTPException(status_code=404, detail="No recommendations generated")

        try:
            # Convert string output to JSON if needed
            if isinstance(recommendations_output, str):
                structured_recommendations = json.loads(recommendations_output)
            else:
                structured_recommendations = recommendations_output

            if not isinstance(structured_recommendations, list):
                structured_recommendations = [structured_recommendations]

            # Add debug logging
            logger.info(f"Structured recommendations: {json.dumps(structured_recommendations)}")

            return RecommendationsResponse(recommendations=structured_recommendations)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.error(f"Raw output: {recommendations_output}")
            raise HTTPException(status_code=500, detail="Invalid JSON format in recommendations")

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=120  # 2 minutes timeout
    )