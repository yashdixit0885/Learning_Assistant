import streamlit as st
import requests
import json

user_input = st.text_area(
    "Enter your learning interests, goals, and current knowledge:",
    placeholder="e.g., Interested in Python programming, want to learn about data analysis, currently know basic syntax.",
)

if st.button("Get Recommendations"):
    backend_url = "https://learning-assistant-a8hc.onrender.com/recommendations/"  # Replace with your actual Render URL
    data = {"user_input": user_input}

    try:
        response = requests.post(backend_url, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        recommendations = response.json()
        # st.write("Full Response:", json.dumps(recommendations, indent=4))  # Print the full response for inspection
        st.subheader("Recommended Learning Resources:")

        # Access the list of recommendations correctly
        if "recommendations" in recommendations and "tasks_output" in recommendations["recommendations"]:
            for task_output in recommendations["recommendations"]["tasks_output"]:
                if task_output["agent"] == "Learning Path Recommendation Specialist":
                    raw_output = task_output["raw"]
                    resources = raw_output.split("\n\n")  # Split resources by double newline
                    for resource in resources:
                        if resource.strip():  # Ensure the resource string is not empty
                            lines = resource.split("\n")
                            title = ""
                            description = ""
                            link = ""
                            rating = ""
                            justification = ""
                            for line in lines:
                                if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
                                    title = line.split(".")[1].strip()
                                elif line.startswith(" * Description:"):
                                    description = line.split(":")[1].strip()
                                elif line.startswith(" * Link:"):
                                    link = line.split(":")[1].strip()
                                elif line.startswith(" * Rating:"):
                                    rating = line.split(":")[1].strip()
                                elif line.startswith(" * Justification:"):
                                    justification = line.split(":")[1].strip()

                            if title and link:
                                st.subheader(title)
                                st.write(f"**Description:** {description}")
                                st.write(f"**Link:** [{link}]({link})") # Create a clickable link
                                if rating:
                                    st.write(f"**Rating:** {rating}")
                                if justification:
                                    st.write(f"**Justification:** {justification}")
                            st.markdown("---") # Add a separator
        else:
            st.error("No recommendations found in the response.")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching recommendations: {e}")