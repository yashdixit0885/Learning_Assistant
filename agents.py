from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from agents import LearningAgents
from crewai import Crew, Process
from pydantic import BaseModel
from typing import List, Optional
import json

# Define Pydantic models for response validation
class Resource(BaseModel):
    title: str
    description: Optional[str] = ""
    link: Optional[str] = ""
    rating: Optional[str] = ""
    justification: Optional[str] = ""

class RecommendationsResponse(BaseModel):
    recommendations: List[Resource]

# Initialize FastAPI app
app = FastAPI()

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
    print(f"Error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

@app.post("/recommendations/")
async def get_learning_recommendations(user_input: str = Body(embed=True)):
    """
    Receives user input and returns learning resource recommendations.
    """
    print(f"Received user input: {user_input}")

    # Define tasks
    interest_analysis_task = learning_agents.define_interest_analysis_task(user_input)
    resource_search_task = learning_agents.define_resource_search_task("user interests summary")
    resource_evaluation_task = learning_agents.define_resource_evaluation_task("list of resources")
    recommendation_task = learning_agents.define_recommendation_task("evaluated resources")

    # Create the crew
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

    # Run the crew
    result = learning_crew.kickoff()
    print(f"Crew result: {result}")

    # Find the output of the recommendation task
    recommendations_output = None
    for task in learning_crew.tasks:
        print(f"Task description: {task.description}")
        print(f"Task output: {task.output}")
        if task.description.startswith("Compile a personalized list of learning resources"):
            recommendations_output = task.output
            break

    if recommendations_output is None:
        print("Warning: No recommendation task output found")
        return {"error": "No recommendations generated"}

    print(f"Raw recommendations_output: {recommendations_output}")

    structured_recommendations = []
    if recommendations_output:
        try:
            # First try parsing as JSON
            structured_recommendations = json.loads(recommendations_output)
            print(f"Parsed JSON structure: {type(structured_recommendations)}")
            
            if not isinstance(structured_recommendations, list):
                print(f"Unexpected JSON structure: {structured_recommendations}")
                if isinstance(structured_recommendations, dict):
                    structured_recommendations = [structured_recommendations]
                else:
                    raise ValueError("Invalid JSON structure")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Parsing error: {e}")
            print("Falling back to text parsing")
            resources = recommendations_output.split("\n\n")
            for resource in resources:
                if not resource.strip():
                    continue
                
                lines = resource.split("\n")
                current_resource = {
                    "title": "",
                    "description": "",
                    "link": "",
                    "rating": "",
                    "justification": ""
                }
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("Title:"):
                        current_resource["title"] = line[6:].strip()
                    elif line.startswith("Description:"):
                        current_resource["description"] = line[12:].strip()
                    elif line.startswith("Link:"):
                        current_resource["link"] = line[5:].strip()
                    elif line.startswith("Rating:"):
                        current_resource["rating"] = line[7:].strip()
                    elif line.startswith("Justification:"):
                        current_resource["justification"] = line[14:].strip()
                
                if current_resource["title"] or current_resource["description"]:
                    structured_recommendations.append(current_resource)

    print(f"Final structured recommendations: {structured_recommendations}")
    
    try:
        # Validate response using Pydantic model
        response = RecommendationsResponse(recommendations=structured_recommendations)
        return response.dict()
    except Exception as e:
        print(f"Error validating response: {e}")
        return {"error": "Invalid response structure", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)