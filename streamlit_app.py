from lyzr import DataAnalyzr, DataConnector
import streamlit as st
import pandas as pd
import io
import re

error_messages = []

UPLOADED_FILE_KEY = "uploaded_csv"
API_KEY = "api_key"

def validate_api_key(key):
    """Function to validate the OpenAI API key"""
    return re.match(r"^sk-[a-zA-Z0-9]{48}$", key) is not None

placeholder_text = (
    "You can find your OpenAI API key here: https://platform.openai.com/api-keys"
)

openai_api_key = st.text_input(
    "Enter your OpenAI API key:", value="", help=placeholder_text
)

if openai_api_key:
    if validate_api_key(openai_api_key):
        st.session_state[
            API_KEY
        ] = openai_api_key
    else:
        error_messages.append("The API key is invalid. Please enter a valid OpenAI API key.")
        openai_api_key = None
else:
    error_messages.append("Please enter an OpenAI API key.")


uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

df = pd.DataFrame()

if uploaded_file is not None:
    st.session_state[UPLOADED_FILE_KEY] = uploaded_file
    try:
        df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        error_messages.append("The CSV file is empty.")
    except pd.errors.ParserError as e:
        error_messages.append(f"An error occurred parsing the CSV file: {e}")
    except Exception as e:
        error_messages.append(f"An error occurred when reading the CSV file: {e}")

if UPLOADED_FILE_KEY in st.session_state:
    uploaded_file = st.session_state[UPLOADED_FILE_KEY]
else:
    error_messages.append("Please upload a CSV file")


if not error_messages and uploaded_file:
    try:
        data_analyzr = DataAnalyzr(df=df, api_key=openai_api_key)
    except Exception as e:
        st.error(f"Error while initializing DataAnalyzr: {e}")

    analysis_query = st.text_input("### Enter your query related to the data:")
    analyze_clicked = st.button('Analyze')

    if analyze_clicked and analysis_query:
        with st.spinner("Analyzing..."):
            try:
                analysis = data_analyzr.analysis_insights(user_input=analysis_query)
                st.write(analysis)
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

    visualization_query = st.text_input("### Enter visualization query related to the data:")
    visualize_clicked = st.button('Visualize')
 
    if visualize_clicked and visualization_query:
        with st.spinner("Visualizing..."):
            try:
                visualizations = data_analyzr.visualizations(user_input=visualization_query)
                for image_name, image_bytes in visualizations.items():
                    image = io.BytesIO(image_bytes)
                    st.image(image, use_column_width=True)
            except Exception as e:
                st.error(f"An error occurred during visualization: {e}")

else:
    for error in error_messages:
        st.error(error)