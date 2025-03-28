import streamlit as st
import requests

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
        st.subheader("Recommended Learning Resources:")

        # Access the list of recommendations correctly
        if "recommendations" in recommendations:
            for recommendation in recommendations["recommendations"]:
                st.write(recommendation)
        else:
            st.error("No recommendations found in the response.")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching recommendations: {e}")