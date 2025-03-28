from fastapi import FastAPI, Body
from agents import LearningAgents
from crewai import Crew, Process

app = FastAPI()
learning_agents = LearningAgents()

@app.post("/recommendations/")
async def get_learning_recommendations(user_input: str = Body(embed=True)):
    """
    Receives user input and returns learning resource recommendations.
    """
    # Define tasks
    interest_analysis_task = learning_agents.define_interest_analysis_task(user_input)
    resource_search_task = learning_agents.define_resource_search_task(interest_analysis_task.expected_output)
    resource_evaluation_task = learning_agents.define_resource_evaluation_task(resource_search_task.expected_output)
    recommendation_task = learning_agents.define_recommendation_task(resource_evaluation_task.expected_output)

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
    recommendations = learning_crew.kickoff()

    return {"recommendations": recommendations}