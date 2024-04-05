import base64
import pandas as pd
import streamlit as st

def calculate_grades(df):
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    subjects = df.columns.tolist()[1:]

    df['TOTAL MARKS'] = df[subjects].sum(axis=1)

    df = df.sort_values(by='TOTAL MARKS', ascending=False)
    df['Rank'] = range(1, len(df) + 1)

    df.set_index('Rank', inplace=True)

    return df

def create_mean_scores_table(df):
    df = df.iloc[:, 1:-1]  # Exclude the first and last columns

    mean_scores = df.mean()
    sorted_scores = mean_scores.sort_values(ascending=False)

    mean_scores_df = pd.DataFrame({"Subject": sorted_scores.index, "Mean Score": sorted_scores.values})
    
    return mean_scores_df

def search_and_filter(student_name, df):
    student_data = df.query("NAMES == @student_name")
    if not student_data.empty:
        st.write("Results for student:", student_name)
        st.write(student_data[['NAMES', 'ENG', 'KISW', 'MATHS', 'INTEG SCINCE', 'SST/CRE', 'TOTAL MARKS']])
    else:
        st.write("Student not found.")

def page1():
    st.title('Student Grade Calculator')

    st.markdown("""
    <style>
    body {
        color: #fff;
        background-color: #4f8bf9;
    }
    </style>
        """, unsafe_allow_html=True)

    st.write("Please upload a CSV or Excel file with student grades:")

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
        except Exception as e:
            data = pd.read_excel(uploaded_file)
        
        if 'NAMES' not in data.columns:
            st.error("File must contain a 'NAMES' column.")
            return
        
        st.markdown("**Data has been successfully uploaded.**")  

        if st.button('Calculate Grades'):
            result = calculate_grades(data)
            st.session_state['result'] = result  # Save the result in the session state

            # Create two columns
            col1, col2 = st.columns(2)

            with col1:
                st.header("Ranking Table")
                st.write(result) 

            with col2:
                st.header("Mean Scores by Subject")
                mean_scores_table = create_mean_scores_table(result)
                st.write(mean_scores_table)

def page2():
    st.title('Student Performance Analysis')

    if 'result' in st.session_state:
        result = st.session_state['result']

        st.header("Student Search and Filter:")
        selected_student = st.selectbox("Select student name:", result['NAMES'].unique())
        search_button = st.button("Search")
        if search_button:
            search_results_placeholder = st.empty()
            search_and_filter(selected_student, result)  
            search_results_placeholder.markdown("")  
    else:
        st.write("No data available. Please calculate grades on the first page.")


pages = {
    "Student Grade Calculator": page1,
    "Student Performance Analysis": page2,
}

# Render the page selection as a radio button in the sidebar
selected_page = st.sidebar.radio("Select your page:", tuple(pages.keys()))


pages[selected_page]()
