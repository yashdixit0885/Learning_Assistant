# agents.py
import warnings
warnings.filterwarnings('ignore') # Ignore warnings

import os
import sys
sys.stderr = open(os.devnull, 'w') # Silence stderr

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import os
import google.generativeai as genai
from crewai_tools import SerperDevTool

from crewai import LLM

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    max_tokens=1000,
)


load_dotenv()

# Configure the Gemini LLM
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    print("Warning: GEMINI_API_KEY not found in environment variables. Gemini integration will not work.")
else:
    genai.configure(api_key=gemini_api_key)
    gemini_llm = genai.GenerativeModel("gemini-pro") # You can choose other Gemini models

class LearningAgents():
    def interest_analyzer_agent(self):
        return Agent(
            role='Learning Interest Analyst',
            goal='Understand the user\'s learning interests, goals, and current knowledge to provide effective recommendations.',
            backstory="""You are an expert in identifying learning needs and preferences. You have a knack for asking insightful questions to fully grasp what someone wants to learn and their current level of understanding. Your ultimate goal is to help the user discover the best learning resources available.""",
            verbose=True,
            allow_delegation=False, # For this initial agent, we don't want it to delegate yet
            llm=llm,
            tools=[
                SerperDevTool(
                    name="Google Search",
                    description="Search the web for relevant learning resources.",
                    search_engine="Google",
                    max_results=5,  # Limit to 5 results for simplicity
                    verbose=True
                )
            ],
        )

    def resource_searcher_agent(self):

        return Agent(
            role='Learning Resource Searcher',
            goal='Find relevant and high-quality learning resources (courses, articles, videos, etc.) on the web based on the user\'s interests and goals.',
            backstory="""You are a highly skilled research assistant with expertise in finding educational content online. You know how to use search engines effectively to discover a wide range of resources, from beginner-friendly introductions to advanced materials. Your aim is to provide the user with a diverse set of options to further their learning.""",
            verbose=True,
            allow_delegation=False, # For now, this agent will not delegate
            llm=llm,
            tools=[
                SerperDevTool(
                    name="Google Search",
                    description="Search the web for relevant learning resources.",
                    search_engine="Google",
                    max_results=5,  # Limit to 5 results for simplicity
                    verbose=True
                )
            ],
        )
    def resource_evaluator_agent(self):
        return Agent(
            role='Learning Resource Evaluator',
            goal='Assess the quality, relevance, and suitability of learning resources based on the user\'s needs and goals.',
            backstory="""You are a meticulous and critical evaluator of educational content. You have a keen eye for detail and can quickly determine if a resource is credible, up-to-date, and appropriate for the user's learning level. You consider factors like the source's reputation, the content's clarity, and the practical value it offers.""",
            verbose=True,
            allow_delegation=False, # For now, this agent will not delegate
            llm=llm,
            tools=[
                SerperDevTool(
                    name="Google Search",
                    description="Search the web for relevant learning resources.",
                    search_engine="Google",
                    max_results=5,  # Limit to 5 results for simplicity
                    verbose=True
                )
            ],
            # We might add tools for more advanced evaluation later (e.g., accessing user reviews)
        )

    def recommendation_agent(self):
        return Agent(
            role='Learning Path Recommendation Specialist',
            goal='Compile a personalized list of learning resources, prioritizing quality and relevance, and present it in a clear, concise, and user-friendly format.',
            backstory="""You are a highly organized and insightful learning curator. You excel at synthesizing information from various sources and presenting it in a way that is both informative and engaging. You understand the importance of clear structure and actionable recommendations to maximize the learner's success.""",
            verbose=True,
            allow_delegation=False, # This agent is the final output agent
            llm=llm,
            tools=[
                SerperDevTool(
                    name="Google Search",
                    description="Search the web for relevant learning resources.",
                    search_engine="Google",
                    max_results=5,  # Limit to 5 results for simplicity
                    verbose=True
                )
            ],
        )

    def define_interest_analysis_task(self, user_input):
        return Task(
            description=f"""
            Analyze the user's input: '{user_input}'.
            Identify their learning interests, goals, and current knowledge level.
            Provide a clear summary of their learning needs.
            """,
            agent=self.interest_analyzer_agent(),
            expected_output="A concise summary of the user's learning interests, goals, and current knowledge.",
        )

    def define_resource_search_task(self, interests_summary):
        return Task(
            description=f"""
            Search the web for relevant learning resources based on the following user learning needs: '{interests_summary}'.
            Find a variety of resources, including online courses, articles, videos, tutorials, and documentation.
            Limit search results to 5 resources.
            """,
            agent=self.resource_searcher_agent(),
            expected_output="A list of 5 relevant learning resources with titles, descriptions, and links.",
        )

    def define_resource_evaluation_task(self, resources):
        return Task(
            description=f"""
            Evaluate the following learning resources for quality, relevance, and suitability: '{resources}'.
            Consider factors such as the source's credibility, content clarity, and practical value.
            Provide a rating and brief justification for each resource.
            """,
            agent=self.resource_evaluator_agent(),
            expected_output="An evaluation of each resource with a rating and justification.",
        )

    def define_recommendation_task(self, evaluated_resources):
        return Task(
            description=f"""
            Compile a personalized list of learning resources based on the following evaluated resources: '{evaluated_resources}'.
            Prioritize the highest-rated resources and present them as a JSON-like structure (list of dictionaries) with keys: "title", "description", "link", "rating", "justification".
            """,
            agent=self.recommendation_agent(),
            expected_output="A JSON-like list of recommended learning resources.",
        )

