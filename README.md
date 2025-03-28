# Personalized Learning Assistant

## Description

This project is a web application that acts as a personalized learning assistant. It uses AI agents to analyze user input about their learning interests, goals, and current knowledge, and provides a curated list of relevant learning resources. The application is built using CrewAI for agent orchestration and FastAPI for the backend API.

## Table of Contents

- [Features](#features)
- [Agents](#agents)
- [Usage](#usage)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Features

-   **User Interest Analysis:** The application analyzes user input to understand their learning needs.
-   **Resource Search:** AI agents search the web for relevant learning resources.
-   **Resource Evaluation:** AI agents evaluate the quality and relevance of found resources.
-   **Personalized Recommendations:** The application provides a curated list of learning resources tailored to the user.
-   **Web API:** The application exposes its functionality through a web API.

## Agents

The application uses the following AI agents:

-   **Learning Interest Analyst:** Understands user learning needs and goals.
-   **Resource Searcher:** Searches the web for learning resources.
-   **Resource Evaluator:** Assesses the quality and relevance of resources.
-   **Learning Path Recommendation Specialist:** Compiles a personalized list of recommendations.

## Usage

To use the application, send a POST request to the `/recommendations/` endpoint with a JSON body containing the user's input:

json
{
  "user_input": "I want to learn Python for data science. I'm a beginner."
}

## Installation

1.  Clone the repository:
    ```bash
    git clone <your_repository_url>
    ```
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up API keys:
    * Create a `.env` file and add your Gemini API key:
        ```
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY
        ```
    * You might also need an OpenAI API key for some tools (if you haven't already set it up).
5.  Run the application:
    ```bash
    uvicorn main:app --reload
    ```

## API Reference

### POST /recommendations/

Receives user input and returns learning resource recommendations.

**Request Body:**

json
{
  "user_input": "string"  // User's learning interests, goals, and current knowledge.
}

{
  "recommendations": [
    // ... your learning resource recommendations (JSON array)
  ]
}

## Deployment

This application is deployed on Render. You can access it at: [https://learning-assistant-a8hc.onrender.com/recommendations/]

For deployment instructions, see https://render.com/docs/projects.

## Contributing

If you'd like to contribute to this project, please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your changes.
3.  Make your changes and commit them.
4.  Submit a pull request.

## License

This project is licensed under the MIT, Apache 2.0 License.