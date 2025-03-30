import streamlit as st
import requests
import json
import time

# Page configuration
st.set_page_config(
    page_title="Learning Assistant",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("🎓 Learning Assistant")
st.markdown("""
This tool helps you find personalized learning resources based on your interests and goals.
Just describe what you'd like to learn, and we'll do the rest!
""")

# Add sidebar for filters and preferences
with st.sidebar:
    st.header("Preferences")
    
    # Resource type filter
    resource_types = st.multiselect(
        "Resource Types",
        ["Videos", "Articles", "Courses", "Books", "Interactive"],
        default=["Videos", "Articles", "Courses"]
    )
    
    # Difficulty level
    difficulty = st.select_slider(
        "Preferred Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Beginner"
    )
    
    # Time commitment
    max_time = st.slider(
        "Maximum Time Commitment (hours/week)",
        min_value=1,
        max_value=20,
        value=5
    )

# Modify the user input section
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        user_input = st.text_area(
            "Enter your learning interests, goals, and current knowledge:",
            placeholder="e.g., Interested in Python programming, want to learn about data analysis, currently know basic syntax.",
            height=150
        )
    with col2:
        st.markdown("### Quick Tags")
        selected_tags = st.multiselect(
            "",
            ["Programming", "Data Science", "Web Development", "AI/ML", "DevOps"],
            placeholder="Select relevant areas"
        )

def display_resource(idx, resource):
    """Helper function to display a single resource"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {idx}. {resource.get('title', 'Untitled')}")
            
            # Display description without JSON formatting
            description = resource.get('description', 'No description available')
            if description.startswith('```json'):
                description = "No description available"
            st.markdown(f"**Description:** {description}")
            
            if link := resource.get('link'):
                st.markdown(f"**Link:** [{link}]({link})")
            
            if justification := resource.get('justification'):
                with st.expander("Why this resource?"):
                    st.write(justification)
            
            # Add resource metadata
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                st.caption(f"Type: {resource.get('type', 'N/A')}")
            with meta_col2:
                st.caption(f"Duration: {resource.get('duration', 'N/A')}")
            with meta_col3:
                st.caption(f"Difficulty: {resource.get('difficulty', 'N/A')}")
            
            # Add feedback buttons
            feedback_col1, feedback_col2, feedback_col3 = st.columns(3)
            with feedback_col1:
                if st.button(f"👍 Helpful #{idx}"):
                    st.toast("Thank you for your feedback!")
            with feedback_col2:
                if st.button(f"🔖 Save #{idx}"):
                    st.toast("Resource saved!")
            with feedback_col3:
                if st.button(f"👎 Not relevant #{idx}"):
                    st.toast("Thanks for letting us know!")
        
        with col2:
            if rating := resource.get('rating'):
                if isinstance(rating, (int, float)):
                    st.info(f"Rating: {'⭐' * int(rating)}")
                else:
                    st.info(f"Rating: {rating}")
        
        st.markdown("---")

# Process button
if st.button("Get Recommendations", type="primary"):
    if not user_input.strip():
        st.error("Please enter your learning interests before submitting.")
        st.stop()

    with st.spinner("🔍 Analyzing your interests and finding the best learning resources..."):
        try:
            # Prepare request payload with all preferences
            payload = {
                "user_input": user_input,
                "domains": selected_tags,  # Add selected domains/tags
                "preferences": {
                    "resource_types": resource_types,
                    "difficulty": difficulty,
                    "max_time": max_time
                }
            }
            
            # Make API request
            backend_url = "http://localhost:8000/recommendations/"
            response = requests.post(
                backend_url,
                json=payload,
                timeout=130
            )
            response.raise_for_status()
            recommendations = response.json()

            # Debug information (hidden by default)
            with st.expander("🔧 Debug Information"):
                st.code(json.dumps(recommendations, indent=2))

            # Display recommendations
            if "recommendations" in recommendations and recommendations["recommendations"]:
                st.success("✨ Found relevant learning resources for you!")
                
                for idx, resource in enumerate(recommendations["recommendations"], 1):
                    try:
                        # Get description and clean it up
                        description = resource.get('description', '')
                        if description.startswith('```json'):
                            # Extract JSON content between backticks and clean it
                            json_str = description.split('```json')[1].split('```')[0].strip()
                            # Clean up any potential formatting issues
                            json_str = json_str.replace('\n', ' ').replace('\r', '')
                            parsed_resources = json.loads(json_str)
                            
                            if isinstance(parsed_resources, list):
                                for parsed_idx, parsed_resource in enumerate(parsed_resources, idx):
                                    display_resource(parsed_idx, parsed_resource)
                            else:
                                display_resource(idx, parsed_resources)
                        else:
                            display_resource(idx, resource)
                            
                    except json.JSONDecodeError as e:
                        st.warning(f"Could not parse recommendation {idx}. Displaying as plain text.")
                        display_resource(idx, resource)
                    except Exception as e:
                        st.error(f"Error processing recommendation {idx}: {str(e)}")
                        continue

        except requests.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.RequestException as e:
            st.error(f"❌ Error fetching recommendations: {str(e)}")
            st.info("Please try again in a few moments.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.info("Please try again or contact support if the issue persists.")



# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Your Learning Assistant Team")