"""
Streamlit demo for DataAnalyzr
"""
import re
import io
import ast
import pandas as pd
import streamlit as st
from io import StringIO
from lyzr import DataAnalyzr

st.image("./assets/Lyzr-Logo.webp", width=150)
st.markdown("#### DataAnalyzr by Lyzr")

# Define the key for the uploaded file and the API key in session_state
UPLOADED_FILE_KEY = "uploaded_csv"
API_KEY = "api_key"


def validate_api_key(key):
    """Function to validate the OpenAI API key"""
    return re.match(r"^sk-[a-zA-Z0-9]{48}$", key) is not None


def format_recommendations_to_markdown(recommendations_str):
    """Function to format recommendations to markdown"""
    markdown_string = ""
    for rec in recommendations_str:
        markdown_string += "**Recommendation:** {}\n".format(rec["Recommendation"])
        markdown_string += "**Basis of the Recommendation:** {}\n".format(
            rec["Basis of the Recommendation"]
        )
        markdown_string += "**Impact if implemented:** {}\n\n".format(
            rec["Impact if implemented"]
        )
    return markdown_string


error_messages = []

SIDEBAR_TEXT = """
- This App is developed by [lyzr.ai](https://www.lyzr.ai/) and powered by Lyzr's DataAnalyzr.
- Learn more about DataAnalyzr and other SDKs at [Lyzr Documentation](https://docs.lyzr.ai/Lyzr%20SDKs/intro)
- To Book a Demo or to Contact Us, click [here](https://www.lyzr.ai/book-demo/)
"""

# Initialize a variable to hold the OpenAI API key
openai_api_key = None

# Check if the user has previously entered a valid API key and store it
if API_KEY in st.session_state and validate_api_key(st.session_state[API_KEY]):
    openai_api_key = st.session_state[API_KEY]

# Sidebar expander for the OpenAI API Key input
with st.sidebar.expander("OpenAI API Key"):
    placeholder_text = (
        "You can find your OpenAI API key here: https://platform.openai.com/api-keys"
    )
    input_key = st.text_input(
        "Enter your OpenAI API key:", value=openai_api_key or "", help=placeholder_text
    )

    # Validate the API key if provided
    if input_key:
        if validate_api_key(input_key):
            openai_api_key = input_key
            st.session_state[
                API_KEY
            ] = openai_api_key  # Save valid key to session state
        else:
            st.error("The API key is invalid. Please enter a valid OpenAI API key.")
            openai_api_key = None  # Reset the variable if key is invalid
    else:
        # Prompt the user to enter an API key if it's not entered
        error_messages.append("Please enter an OpenAI API key.")

st.sidebar.markdown(SIDEBAR_TEXT)


uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
df = pd.DataFrame()

# Check if the user has uploaded a file and, if so, save it to the session state
if uploaded_file is not None:
    st.session_state[UPLOADED_FILE_KEY] = uploaded_file

# If the user has previously uploaded a file, it will be retrieved from the session state
if UPLOADED_FILE_KEY in st.session_state:
    uploaded_file = st.session_state[UPLOADED_FILE_KEY]
else:
    # If there's no file uploaded, add this message to the error_messages list
    error_messages.append("Please upload a CSV file")


# Check if the uploaded file is ready to be processed
if uploaded_file is not None:
    try:
        # Since UploadedFile behaves like a file-like object, use StringIO to convert it to a StringIO object
        # This is required to help pandas recognize it as a file-like object
        # This code assumes that the CSV file is comma-delimited
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
    except pd.errors.EmptyDataError:
        error_messages.append("The CSV file is empty.")
    except pd.errors.ParserError as e:
        error_messages.append(f"An error occurred parsing the CSV file: {e}")
    except Exception as e:
        error_messages.append(f"An error occurred when reading the CSV file: {e}")


if not error_messages and uploaded_file:
    data_analyzr = DataAnalyzr(df=df, api_key=openai_api_key)

    query = st.text_input("### Enter your query related to the data:")

    cols = st.columns([2, 2, 10])
    with cols[0]:
        analyze_clicked = st.button("Analyze")
    with cols[1]:
        visualize_clicked = st.button("Visualize")

    # Define keys for results in session state
    ANALYSIS_RESULTS_KEY = "analysis_results"
    VISUALIZATION_RESULTS_KEY = "visualization_results"

    if analyze_clicked and query:
        with st.spinner("Analyzing..."):
            try:
                data_analyzr = DataAnalyzr(df=df, api_key=openai_api_key)
                st.write(df)
                # Perform analysis and write to session state
                analysis = data_analyzr.analysis_insights(
                    user_input=query
                )
                st.write(analysis)
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

    elif visualize_clicked and query:
        with st.spinner("Visualizing..."):
            try:
                visualizations = data_analyzr.visualizations(user_input=query)
                for image_name, image_bytes in visualizations.items():
                    image = io.BytesIO(image_bytes)
                    st.image(image, use_column_width=True)
                    st.success("Visualization complete!")
            except Exception as e:
                st.error(f"An error occurred during visualization: {e}")

    with st.expander("More"):
        st.markdown("Analysis Suggestions:")
        suggestions_clicked = st.button("Get Suggestions")
        if suggestions_clicked:
            with st.spinner("Generating Suggestions..."):
                try:
                    suggestions = data_analyzr.analysis_recommendation()
                    st.write(suggestions)
                except Exception as e:
                    st.error(f"An error occurred during generation: {e}")

        st.markdown("Describe Data")
        describe_clicked = st.button("Describe Data")
        if describe_clicked:
            with st.spinner("Describing..."):
                try:
                    description = data_analyzr.dataset_description()
                    st.write(description)
                except Exception as e:
                    st.error(f"An error occurred during description: {e}")
                else:
                    st.success("Description complete!")

        st.markdown("Get Queries for different types of Analysis")
        queries_clicked = st.button("Get Queries")
        if queries_clicked:
            with st.spinner("Getting Queries..."):
                try:
                    ai_queries = data_analyzr.ai_queries_df()
                    st.write(ai_queries)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                else:
                    st.success("Description complete!")

        recommendations_query = st.text_input(
            "strategic recommendations based on analysis insights:",
            key="recommendations",
        )
        recommendations_clicked = st.button(
            "Recommendations", key="recommendations_btn"
        )

        if recommendations_clicked and recommendations_query:
            with st.spinner("Generating Recommendations..."):
                try:
                    recommendations = data_analyzr.recommendations(
                        user_input=recommendations_query
                    )
                    recommendations = ast.literal_eval(recommendations.strip())
                    formatted_recommendations_markdown = (
                        format_recommendations_to_markdown(recommendations)
                    )
                    st.write(formatted_recommendations_markdown, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        tasks_query = st.text_input(
            "Transform insights and recommendations into actionable tasks", key="tasks"
        )
        tasks_clicked = st.button("tasks", key="tasks_btn")

        if tasks_clicked and tasks_query:
            with st.spinner("Generating tasks..."):
                try:
                    tasks = data_analyzr.tasks(user_input=tasks_query)
                    st.write(tasks)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

else:
    for error in error_messages:
        st.error(error)
