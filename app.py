import streamlit as st
import pandas as pd
from io import BytesIO
import base64

def calculate_grades(df):
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    subjects = df.columns.tolist()[1:]

    df['TOTAL MARKS'] = df[subjects].sum(axis=1)

    df = df.sort_values(by='TOTAL MARKS', ascending=False)
    df['Rank'] = range(1, len(df) + 1)

    df.set_index('Rank', inplace=True)

    return df

st.title('Student Grade Calculator')

# Instruction
st.write("Please upload a CSV or Excel file with student grades:")

uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
    except Exception as e:
        data = pd.read_excel(uploaded_file)
    st.write("Data has been successfully uploaded.")  

    if st.button('Calculate Grades'):
        result = calculate_grades(data)
        st.write(result) 
 
