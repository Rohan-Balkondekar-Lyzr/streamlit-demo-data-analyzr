from lyzr import DataAnalyzr, DataConnector
import streamlit as st
import pandas as pd
import io

openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

df = None
error_messages = []
if uploaded_file is None:
    error_messages.append('Please upload a CSV file.')
if not openai_api_key:
    error_messages.append('Please enter an OpenAI API key.')
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        error_messages.append(f"An error occurred when reading the CSV file: {e}")

if not error_messages and df is not None:
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