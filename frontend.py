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

# User input
user_input = st.text_area(
    "Enter your learning interests, goals, and current knowledge:",
    placeholder="e.g., Interested in Python programming, want to learn about data analysis, currently know basic syntax.",
    height=150
)

# Process button
if st.button("Get Recommendations", type="primary"):
    if not user_input.strip():
        st.error("Please enter your learning interests before submitting.")
        st.stop()

    with st.spinner("🔍 Analyzing your interests and finding the best learning resources..."):
        try:
            # Make API request
            backend_url = "https://learning-assistant-a8hc.onrender.com/recommendations/"
            response = requests.post(
                backend_url,
                json={"user_input": user_input},
                timeout=30
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
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {idx}. {resource.get('title', 'Untitled')}")
                            st.markdown(f"**Description:** {resource.get('description', 'No description available')}")
                            
                            if link := resource.get('link'):
                                st.markdown(f"**Link:** [{link}]({link})")
                            
                            if justification := resource.get('justification'):
                                with st.expander("Why this resource?"):
                                    st.write(justification)
                        
                        with col2:
                            if rating := resource.get('rating'):
                                st.info(f"Rating: {rating}")
                        
                        st.markdown("---")
            else:
                st.warning("No recommendations found. Please try again with more specific interests.")

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