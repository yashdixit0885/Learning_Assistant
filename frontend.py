import streamlit as st
import requests
import json  # Import the json module

user_input = st.text_area(
    "Enter your learning interests, goals, and current knowledge:",
    placeholder="e.g., Interested in Python programming, want to learn about data analysis, currently know basic syntax.",
)

if st.button("Get Recommendations"):
    backend_url = "https://learning-assistant-a8hc.onrender.com/recommendations/"
    data = {"user_input": user_input}

    try:
        response = requests.post(backend_url, json=data)
        response.raise_for_status()
        recommendations = response.json()
        st.write("Full Response:", json.dumps(recommendations, indent=4))
        st.subheader("Recommended Learning Resources:")

        if "recommendations" in recommendations and "tasks_output" in recommendations["recommendations"]:
            for task_output in recommendations["recommendations"]["tasks_output"]:
                if task_output["agent"] == "Learning Path Recommendation Specialist":
                    raw_output = task_output["raw"]
                    resources = raw_output.split("\n\n")
                    
                    for resource in resources:
                        if resource.strip():
                            lines = resource.split("\n")
                            title = description = link = rating = justification = ""
                            
                            for line in lines:
                                if line.startswith(("1.", "2.", "3.", "4.", "5.")):
                                    title = line.split(".", 1)[1].strip()
                                elif line.strip().startswith("* Description:"):
                                    description = line.split(":", 1)[1].strip()
                                elif line.strip().startswith("* Link:"):
                                    link = line.split(":", 1)[1].strip()
                                elif line.strip().startswith("* Rating:"):
                                    rating = line.split(":", 1)[1].strip()
                                elif line.strip().startswith("* Justification:"):
                                    justification = line.split(":", 1)[1].strip()

                            if title and link:
                                st.subheader(title)
                                st.write(f"**Description:** {description}")
                                st.write(f"**Link:** [{link}]({link})")
                                if rating:
                                    st.write(f"**Rating:** {rating}")
                                if justification:
                                    st.write(f"**Justification:** {justification}")
                                st.markdown("---")
        else:
            st.error("No recommendations found in the response")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recommendations: {str(e)}")