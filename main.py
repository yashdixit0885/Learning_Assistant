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
from models import init_db, SessionLocal, Feedback  # import your DB objects

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

class UserPreferences(BaseModel):
    resource_types: List[str]
    difficulty: str
    max_time: int

class UserInput(BaseModel):
    user_input: str
    domains: List[str]
    preferences: UserPreferences
    
# Pydantic model for feedback input
class FeedbackInput(BaseModel):
    user_id: str
    resource_id: str
    feedback: str  # "helpful", "not_relevant", etc.

# Initialize FastAPI app
app = FastAPI(title="Learning Assistant API")
init_db()  # Initialize the database


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

@app.post("/feedback/")
def submit_feedback(data: FeedbackInput):
    """
    Endpoint to collect resource feedback from users.
    """
    db = SessionLocal()
    try:
        # Create a new Feedback row
        feedback_entry = Feedback(
            user_id=data.user_id,
            resource_id=data.resource_id,
            feedback=data.feedback
        )
        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)

        return {"status": "Feedback stored", "record": {
            "id": feedback_entry.id,
            "user_id": feedback_entry.user_id,
            "resource_id": feedback_entry.resource_id,
            "feedback": feedback_entry.feedback
        }}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to process feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing feedback: {str(e)}"
        )
    finally:
        db.close()


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
        logger.info(f"Received request with input: {data}")
        
        if not data.user_input.strip():
            raise HTTPException(status_code=400, detail="User input cannot be empty")

        # Create domain-specific agents for selected domains
        domain_agents = [
            learning_agents.domain_specialist_agent(domain)
            for domain in data.domains
        ]

        # Define tasks with user preferences
        interest_analysis_task = learning_agents.define_interest_analysis_task(data.user_input)
        resource_search_task = learning_agents.define_resource_search_task("user interests summary")
        resource_evaluation_task = learning_agents.define_resource_evaluation_task("list of resources")
        recommendation_task = learning_agents.define_recommendation_task("evaluated resources")
        learning_path_task = learning_agents.define_learning_path_task(
            "interests summary",
            data.preferences.difficulty,
            data.preferences.max_time
        )

        # Create and run crew with domain specialists
        learning_crew = Crew(
            agents=[
                learning_agents.interest_analyzer_agent(),
                learning_agents.resource_searcher_agent(),
                learning_agents.resource_evaluator_agent(),
                learning_agents.recommendation_agent(),
                *domain_agents  # Add domain-specific agents
            ],
            tasks=[
                interest_analysis_task,
                resource_search_task,
                resource_evaluation_task,
                recommendation_task,
                learning_path_task
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

        
                # Process recommendations with enhanced logging
        recommendations_output = None
        try:
            for task in learning_crew.tasks:
                if task.description.startswith("Create JSON array"):
                    logger.info(f"Found recommendation task: {task.description}")
                    
                    # Get the raw output
                    raw_output = task.output
                    logger.info(f"Raw output type: {type(raw_output)}")
                    
                    # Convert raw output to structured recommendations
                    if isinstance(raw_output, str):
                        # Try to parse if it's a JSON string
                        try:
                            structured_recommendations = json.loads(raw_output)
                        except json.JSONDecodeError:
                            # If not valid JSON, try to parse the text format
                            recommendations = []
                            current_rec = {}
                            
                            for line in raw_output.split('\n'):
                                line = line.strip()
                                if line.startswith('Title:'):
                                    if current_rec:
                                        recommendations.append(current_rec)
                                    current_rec = {'title': line[6:].strip()}
                                elif line.startswith('Description:'):
                                    current_rec['description'] = line[12:].strip()
                                elif line.startswith('Link:'):
                                    current_rec['link'] = line[5:].strip()
                                elif line.startswith('Rating:'):
                                    current_rec['rating'] = line[7:].strip()
                                elif line.startswith('Justification:'):
                                    current_rec['justification'] = line[14:].strip()
                            
                            if current_rec:
                                recommendations.append(current_rec)
                            
                            structured_recommendations = recommendations
                    
                    elif isinstance(raw_output, dict):
                        structured_recommendations = [raw_output]
                    elif isinstance(raw_output, list):
                        structured_recommendations = raw_output
                    else:
                        # If output is neither string nor dict/list, create a basic recommendation
                        structured_recommendations = [{
                            'title': 'Generated Recommendation',
                            'description': str(raw_output),
                            'link': '',
                            'rating': '',
                            'justification': 'Generated from raw output'
                        }]

                    # Validate and clean recommendations
                    validated_recommendations = []
                    for rec in structured_recommendations:
                        if isinstance(rec, dict):
                            validated_rec = {
                                'title': rec.get('title', 'Untitled'),
                                'description': rec.get('description', ''),
                                'link': rec.get('link', ''),
                                'rating': rec.get('rating', ''),
                                'justification': rec.get('justification', '')
                            }
                            validated_recommendations.append(validated_rec)

                    if not validated_recommendations:
                        raise ValueError("No valid recommendations could be extracted")

                    return RecommendationsResponse(recommendations=validated_recommendations)

            raise HTTPException(
                status_code=404,
                detail="No recommendation task found in results"
            )

        except Exception as e:
            logger.error(f"Error processing recommendations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing recommendations: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=120  # 2 minutes timeout
    )