import warnings
import logging
import os
import sys
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import google.generativeai as genai
from crewai_tools import SerperDevTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings and stderr
warnings.filterwarnings('ignore')
sys.stderr = open(os.devnull, 'w')

class LearningAgents:
    def __init__(self):
        self.llm = self._initialize_llm()
        self._configure_gemini()

    def _initialize_llm(self):
        try:
            return LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.7,
                max_tokens=1000,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None

    def _configure_gemini(self):
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=gemini_api_key)
            self.gemini_llm = genai.GenerativeModel("gemini-pro")

    def _create_search_tool(self):
        return SerperDevTool(
            name="Google Search",
            description="Search for learning resources",
            search_engine="Google",
            max_results=5,
            verbose=True
        )

    def interest_analyzer_agent(self):
        if not self.llm:
            raise RuntimeError("LLM not properly initialized")
        
        return Agent(
            role='Learning Interest Analyst',
            goal='Understand user learning interests and provide effective recommendations.',
            backstory="""You are an expert in identifying learning needs and preferences. You excel at understanding what someone wants to learn and their current level.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._create_search_tool()]
        )

    def resource_searcher_agent(self):
        return Agent(
            role='Learning Resource Searcher',
            goal='Find relevant and high-quality learning resources based on user interests.',
            backstory="""You are a skilled research assistant specializing in finding educational content online.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._create_search_tool()]
        )

    def resource_evaluator_agent(self):
        return Agent(
            role='Learning Resource Evaluator',
            goal='Assess resource quality and relevance.',
            backstory="""You are a meticulous evaluator of educational content with a keen eye for quality.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._create_search_tool()]
        )

    def recommendation_agent(self):
        return Agent(
            role='Learning Path Recommendation Specialist',
            goal='Create personalized learning resource lists.',
            backstory="""You are an organized learning curator who excels at creating clear, actionable recommendations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._create_search_tool()]
        )

    def define_interest_analysis_task(self, user_input):
        return Task(
            description=f"Analyze user input: '{user_input}'. Identify interests, goals, and knowledge level.",
            agent=self.interest_analyzer_agent(),
            expected_output="A concise summary of learning needs."
        )

    def define_resource_search_task(self, interests_summary):
        return Task(
            description=f"Find resources based on: '{interests_summary}'. Include varied content types.",
            agent=self.resource_searcher_agent(),
            expected_output="List of 5 relevant resources with details."
        )

    def define_resource_evaluation_task(self, resources):
        return Task(
            description=f"Evaluate resources: '{resources}'. Consider credibility and relevance.",
            agent=self.resource_evaluator_agent(),
            expected_output="Evaluation with ratings and justifications."
        )

    def define_recommendation_task(self, evaluated_resources):
        return Task(
            description=f"""Create JSON array from: '{evaluated_resources}'. 
            Include title, description, link, rating, justification for each resource.""",
            agent=self.recommendation_agent(),
            expected_output="JSON formatted resource recommendations."
        )