# frontend.py
import streamlit as st
import requests
import json

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

        if "recommendations" in recommendations and isinstance(recommendations["recommendations"], list):
            for resource in recommendations["recommendations"]:
                title = resource.get("title")
                description = resource.get("description", "")
                link = resource.get("link")
                rating = resource.get("rating", "")
                justification = resource.get("justification", "")

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