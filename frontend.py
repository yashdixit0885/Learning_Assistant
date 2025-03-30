import streamlit as st
import requests
import json

####################################
# Page configuration
####################################
st.set_page_config(
    page_title="Learning Assistant",
    page_icon="📚",
    layout="wide"
)

####################################
# Session state initialization
####################################
if "feedback_history" not in st.session_state:
    st.session_state["feedback_history"] = []
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""
# Keep recommendations loaded so they stay visible after feedback interactions
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []

####################################
# Helper: Store feedback locally & remote
####################################
def store_feedback_local_and_remote(resource_id: str, feedback: str, idx: int):
    """
    Stores feedback locally in session state, then sends it to the backend.
    """
    st.session_state["feedback_history"].append({
        "resource_id": resource_id,
        "feedback": feedback
    })
    user_id = st.session_state["user_id"] or "anonymous"
    payload = {
        "user_id": user_id,
        "resource_id": resource_id,
        "feedback": feedback
    }
    try:
        requests.post("http://localhost:8000/feedback/", json=payload)
        st.toast(f"Feedback for item #{idx} submitted by {user_id}!")
    except:
        st.toast("Could not send feedback to backend.")

####################################
# UI: Title and description
####################################
st.title("🎓 Learning Assistant")
st.markdown("""
This tool helps you find personalized learning resources based on your interests and goals.
Just describe what you'd like to learn, and we'll do the rest!
""")

####################################
# UI: Sidebar for preferences
####################################
with st.sidebar:
    st.header("User Info & Preferences")
    # Let the user specify their own user ID
    st.session_state["user_id"] = st.text_input(
        label="User ID",
        value=st.session_state["user_id"],
        placeholder="Enter your unique user ID"
    )
    resource_types = st.multiselect(
        "Resource Types",
        ["Videos", "Articles", "Courses", "Books", "Interactive"],
        default=["Videos", "Articles", "Courses"]
    )
    difficulty = st.select_slider(
        "Preferred Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Beginner"
    )
    max_time = st.slider(
        "Maximum Time Commitment (hours/week)",
        min_value=1,
        max_value=20,
        value=5
    )

####################################
# UI: Capture user input
####################################
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        user_input = st.text_area(
            "Enter your learning interests, goals, and current knowledge:",
            placeholder="e.g., Interested in Python programming, want to learn data analysis...",
            height=150
        )
    with col2:
        st.markdown("### Quick Tags")
        selected_tags = st.multiselect(
            "",
            ["Programming", "Data Science", "Web Development", "AI/ML", "DevOps"],
            placeholder="Select relevant areas"
        )

####################################
# Helper: Display a single resource
####################################
def display_resource(idx, resource):
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {idx}. {resource.get('title', 'Untitled')}")

            # Clean up description
            description = resource.get('description', 'No description')
            if description.startswith('```json'):
                description = "No description available"
            st.markdown(f"**Description:** {description}")

            if link := resource.get('link'):
                st.markdown(f"**Link:** [{link}]({link})")

            if justification := resource.get('justification'):
                with st.expander("Why this resource?"):
                    st.write(justification)

            # Meta info
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                st.caption(f"Type: {resource.get('type', 'N/A')}")
            with meta_col2:
                st.caption(f"Duration: {resource.get('duration', 'N/A')}")
            with meta_col3:
                st.caption(f"Difficulty: {resource.get('difficulty', 'N/A')}")

            # Feedback buttons
            feedback_col1, feedback_col2, feedback_col3 = st.columns(3)
            with feedback_col1:
                if st.button(f"👍 Helpful #{idx}"):
                    store_feedback_local_and_remote(resource.get("id", f"resource_{idx}"), "helpful", idx)
            with feedback_col2:
                if st.button(f"🔖 Save #{idx}"):
                    st.toast("Resource saved locally (unimplemented behavior).")
            with feedback_col3:
                if st.button(f"👎 Not relevant #{idx}"):
                    store_feedback_local_and_remote(resource.get("id", f"resource_{idx}"), "not_relevant", idx)

        with col2:
            if rating := resource.get('rating'):
                try:
                    int_rating = int(float(rating))
                    st.info(f"Rating: {'⭐' * int_rating}")
                except:
                    st.info(f"Rating: {rating}")

        st.markdown("---")

####################################
# Button: Fetch Recommendations
####################################
if st.button("Get Recommendations", type="primary"):
    if not user_input.strip():
        st.error("Please enter your learning interests before submitting.")
        st.stop()

    with st.spinner("🔍 Analyzing your interests and finding the best learning resources..."):
        payload = {
            "user_input": user_input,
            "domains": selected_tags,
            "preferences": {
                "resource_types": resource_types,
                "difficulty": difficulty,
                "max_time": max_time
            }
        }
        backend_url = "http://localhost:8000/recommendations/"

        try:
            response = requests.post(backend_url, json=payload, timeout=130)
            response.raise_for_status()
            results = response.json()

            # Store in session_state so recommendations remain after re-run
            if "recommendations" in results and results["recommendations"]:
                st.session_state["recommendations"] = results["recommendations"]
            else:
                st.warning("No recommendations found.")
                st.session_state["recommendations"] = []

        except requests.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.RequestException as e:
            st.error(f"❌ Error fetching recommendations: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

####################################
# Display any stored recommendations
####################################
if st.session_state["recommendations"]:
    st.success("✨ Found relevant learning resources!")
    for idx, res_item in enumerate(st.session_state["recommendations"], 1):
        try:
            description = res_item.get('description', '')
            if description.startswith('```json'):
                # Attempt to parse embedded JSON
                json_str = description.split('```json')[1].split('```')[0].strip()
                json_str = json_str.replace('\n', ' ').replace('\r', '')
                parsed = json.loads(json_str)

                if isinstance(parsed, list):
                    for j, parsed_res in enumerate(parsed, start=idx):
                        display_resource(j, parsed_res)
                else:
                    display_resource(idx, parsed)
            else:
                display_resource(idx, res_item)
        except json.JSONDecodeError:
            st.warning(f"Could not parse recommendation {idx}. Displaying as plain text.")
            display_resource(idx, res_item)
        except Exception as e:
            st.error(f"Error processing recommendation {idx}: {str(e)}")

####################################
# Footer
####################################
st.markdown("---")
st.markdown("Made with ❤️ by Your Learning Assistant Team")
