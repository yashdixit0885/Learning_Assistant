import warnings
import logging
import os
import sys
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import google.generativeai as genai
from crewai_tools import SerperDevTool
import contextlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings and stderr
warnings.filterwarnings('ignore')
sys.stderr = open(os.devnull, 'w')

class LearningAgents:
    def __init__(self):
        self.llm = self._initialize_llm()
        with contextlib.redirect_stderr(open(os.devnull, 'w')):
            self._configure_gemini()

    def _initialize_llm(self) -> LLM:
        """Initialize the Gemini LLM with specified parameters."""
        try:
            return LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.7,
                max_tokens=1000,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None

    def _configure_gemini(self) -> None:
        """Configure Gemini with environment-provided API key."""
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_llm = genai.GenerativeModel("gemini-pro")
                logger.info("Gemini LLM successfully configured.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")

    def _create_search_tool(self) -> SerperDevTool:
        """Create and configure a SerperDevTool instance for resource searches."""
        return SerperDevTool(
            name="Google Search",
            description="Search for learning resources",
            search_engine="Google",
            max_results=5,
            verbose=True
        )
        
    def _build_agent(self, role: str, goal: str, backstory: str) -> Agent:
        """Helper to reduce repetitive agent initialization."""
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._create_search_tool()]
        )

    def interest_analyzer_agent(self) -> Agent:
        """Creates an agent to analyze user learning interests."""
        if not self.llm:
            raise RuntimeError("LLM not properly initialized")
        return self._build_agent(
            role='Learning Interest Analyst',
            goal='Understand user learning interests and provide effective recommendations.',
            backstory="""You are an expert in identifying learning needs and preferences.
            You excel at understanding what someone wants to learn and their current level."""
        )

    def resource_searcher_agent(self) -> Agent:
        """Creates an agent to search for learning resources."""
        if not self.llm:
            raise RuntimeError("LLM not properly initialized")
        return self._build_agent(
            role='Learning Resource Searcher',
            goal='Find relevant and high-quality learning resources based on user interests.',
            backstory="""You are a skilled research assistant specializing in finding educational content online.""",
            )

    def resource_evaluator_agent(self) -> Agent:
        """Creates an agent to evaluate learning resources."""
        if not self.llm:
            raise RuntimeError("LLM not properly initialized")
        return self._build_agent(
            role='Learning Resource Evaluator',
            goal='Assess resource quality and relevance.',
            backstory="""You are a meticulous evaluator of educational content with a keen eye for quality.""",
        )

    def recommendation_agent(self) -> Agent:
        """Creates an agent to recommend learning resources."""
        if not self.llm:
            raise RuntimeError("LLM not properly initialized")
        return self._build_agent(
            role='Learning Path Recommendation Specialist',
            goal='Create personalized learning resource lists.',
            backstory="""You are an organized learning curator who excels at creating clear, actionable recommendations.""",
        )

    def domain_specialist_agent(self, domain) -> Agent:
        """Creates a specialist agent for specific learning domains"""
        return self._build_agent(
            role=f'{domain} Learning Specialist',
            goal=f'Provide expert guidance in {domain} learning path creation',
            backstory=f"""You are an expert in {domain} education with years of experience 
            in curriculum development and teaching.""",
        )

    def learning_path_creator_agent(self) -> Agent:
        """Creates structured learning paths with prerequisites"""
        return self._build_agent(
            role='Learning Path Architect',
            goal='Create structured learning paths with clear progression',
            backstory="""You are an expert in curriculum design and learning progression. 
            You excel at creating step-by-step learning paths that build upon prerequisites.""",
        )

    def resource_validator_agent(self) -> Agent:
        """Validates and verifies learning resource quality"""
        return self._build_agent(
            role='Resource Quality Validator',
            goal='Ensure resource quality, freshness, and accuracy',
            backstory="""You are a meticulous validator who ensures learning resources 
            are up-to-date, accurate, and of high quality.""",
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

    def define_learning_path_task(self, interests_summary, difficulty, time_commitment):
        return Task(
            description=f"""Create a structured learning path based on:
            Interests: {interests_summary}
            Difficulty: {difficulty}
            Time Commitment: {time_commitment} hours/week""",
            agent=self.learning_path_creator_agent(),
            expected_output="Structured learning path with prerequisites and timeline"
        )