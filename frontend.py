# frontend.py
import streamlit as st
import requests
import json

user_input = st.text_area(
    "Enter your learning interests, goals, and current knowledge:",
    placeholder="e.g., Interested in Python programming, want to learn about data analysis, currently know basic syntax.",
)

# ...existing imports...

if st.button("Get Recommendations"):
    backend_url = "https://learning-assistant-a8hc.onrender.com/recommendations/"
    data = {"user_input": user_input}

    try:
        # Add request debugging
        st.info(f"Sending request with data: {json.dumps(data, indent=2)}")
        
        response = requests.post(backend_url, json=data)
        response.raise_for_status()
        
        # Log raw response for debugging
        st.write("Response Status:", response.status_code)
        
        recommendations = response.json()
        
        # Validate response structure
        if not recommendations:
            st.error("Received empty response from server")
            return
            
        st.write("Response Structure:", type(recommendations))
        st.write("Full Response:", json.dumps(recommendations, indent=4))
        
        st.subheader("Recommended Learning Resources:")

        if "recommendations" in recommendations:
            if not isinstance(recommendations["recommendations"], list):
                st.warning("Recommendations data is not in expected list format")
                st.json(recommendations["recommendations"])
                return
                
            if not recommendations["recommendations"]:
                st.info("No recommendations found in the response")
                return
                
            for resource in recommendations["recommendations"]:
                # Validate each resource
                if not isinstance(resource, dict):
                    continue
                    
                title = resource.get("title", "No Title")
                description = resource.get("description", "No description available")
                link = resource.get("link", "")
                rating = resource.get("rating", "Not rated")
                justification = resource.get("justification", "No justification provided")

                with st.expander(f"📚 {title}"):
                    st.write(f"**Description:** {description}")
                    if link:
                        st.write(f"**Link:** [{link}]({link})")
                    st.write(f"**Rating:** {rating}")
                    st.write(f"**Justification:** {justification}")
        else:
            st.error("Response does not contain 'recommendations' key")
            st.json(recommendations)  # Show full response for debugging

    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        st.exception(e)  # This will show the full traceback