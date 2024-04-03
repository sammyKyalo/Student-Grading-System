import streamlit as st
import pandas as pd
from io import BytesIO
import base64

def calculate_grades(df):
    # Convert the marks columns to integers
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Get the subjects from the column titles, excluding 'NAMES'
    subjects = df.columns.tolist()[1:]

    # Calculate total marks for each student
    df['TOTAL MARKS'] = df[subjects].sum(axis=1)

    # Sort by total marks and add a Rank column
    df = df.sort_values(by='TOTAL MARKS', ascending=False)
    df['Rank'] = range(1, len(df) + 1)

    # Set 'Rank' as the index
    df.set_index('Rank', inplace=True)

    return df

# Title of the app
st.title('Student Grade Calculator')

# Instruction
st.write("Please upload a CSV or Excel file with student grades:")

# File uploader allows user to upload their CSV or Excel file
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
    except Exception as e:
        data = pd.read_excel(uploaded_file)
    st.write(data)  # Display the dataframe

    if st.button('Calculate Grades'):
        result = calculate_grades(data)
        st.write(result)  # Display the result dataframe
