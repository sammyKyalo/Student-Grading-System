import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import time

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
    df = df.iloc[:, 1:-1] 

    mean_scores = df.mean()
    sorted_scores = mean_scores.sort_values(ascending=False)

    mean_scores_df = pd.DataFrame({"Subject": sorted_scores.index, "Mean Score": sorted_scores.values})
    
    return mean_scores_df

def create_mean_scores_plot(df):
    df = df.iloc[:, 1:-1] 

    mean_scores = df.mean()
    sorted_scores = mean_scores.sort_values(ascending=False)

    plt.figure(figsize=(10, 6), frameon=False)  # Set frameon to False
    sns.set_theme(style="darkgrid")  
    ax = sns.barplot(x=sorted_scores.index, y=sorted_scores.values, palette='viridis')
    plt.xlabel('Subjects', color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.ylabel('Mean Score', color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.title('Mean Scores by Subject', color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.xticks(rotation=90, color='white')
    plt.yticks(color='white')
    plt.tight_layout()

    ax.set_facecolor('#000000')
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False) 
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    return plt


def search_and_filter(student_name, df):
    student_data = df.query("NAMES == @student_name")
    if not student_data.empty:
        st.write("Results for student:", student_name)
        # Display all available subjects dynamically
        subjects = [col for col in student_data.columns if col != 'NAMES' and col != 'TOTAL MARKS']
        st.write(student_data[['NAMES'] + subjects + ['TOTAL MARKS']])
    else:
        st.write("Student not found.")


def page1():
    st.title('Student Grading System')

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
            st.session_state['result'] = result  

            col1, col2 = st.columns(2)

            with col1:
                st.header("Mean Scores Plot")
                mean_scores_plot = create_mean_scores_plot(result)
                st.pyplot(mean_scores_plot) 

            with col2:
                st.header("Mean Scores by Subject")
                mean_scores_table = create_mean_scores_table(result)
                st.table(mean_scores_table)

           
            st.header("Result Table")
            st.table(result)
            
            hide_sidebar()

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

def manual_page():
    st.title('Application Manual')

    st.markdown("""
    # Student Grading System Application Manual

    ## Overview
    This application is designed to analyze student grades. It consists of two main pages: `Student Grade Calculator` and `Student Performance Analysis`.

    ## Page 1: Student Grade Calculator

    1. **Upload a File**: The application accepts CSV or Excel files containing student grades. The file must contain a column named 'NAMES'. To upload a file, click on the "Choose a file" button and select the desired file from your device.

    2. **Calculate Grades**: After successfully uploading a file, click on the 'Calculate Grades' button. The application will calculate the total marks for each student and rank them accordingly.

    3. **Mean Scores Plot**: This plot visualizes the mean scores of all subjects. It helps to understand the overall performance of the students in each subject.

    4. **Mean Scores by Subject**: This table displays the mean scores of all subjects in descending order.

    5. **Result Table**: This table displays the calculated total marks and ranks of all students.

    ## Page 2: Student Performance Analysis

    1. **Student Search and Filter**: You can select a student name from the dropdown menu and click on the 'Search' button. The application will display the selected student's scores in all subjects and their total marks.

    Please note that the 'Student Performance Analysis' page requires data from the 'Student Grade Calculator' page. If no data is available, you will be prompted to calculate grades on the first page.

    ## General Usage Notes

    - The application uses a dark theme for better visibility. The text color is white and the background color is blue.

    - The sidebar contains a radio button for navigating between the two pages.

    - The application is designed to hide the sidebar and the Streamlit menu after a few seconds of inactivity.

    - The application layout is set to 'wide' for better utilization of screen space.

    This manual should help you navigate and use the application effectively.
    """, unsafe_allow_html=True)


def hide_sidebar():
    if st.sidebar:
        time.sleep(3) 
        st.sidebar.empty() 

st.set_page_config(layout="wide")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

pages = {
    "Student Grade Calculator": page1,
    "Student Performance Analysis": page2,
    "Manual": manual_page,
}

selected_page = st.sidebar.radio("Select your page:", tuple(pages.keys()))

pages[selected_page]()
