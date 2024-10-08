import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import time
import logging
import gspread
import os
import google.oauth2.credentials
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import json

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .reportview-container {
        background: #202020;
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def calculate_grades(df):
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    subjects = df.columns.tolist()[1:]

    df['TOTAL MARKS'] = df[subjects].sum(axis=1).round(2)

    df = df.sort_values(by='TOTAL MARKS', ascending=False)
    df['Rank'] = range(1, len(df) + 1)

    df = df.set_index('Rank')  

    return df



def create_mean_scores_table(df):
    df = df.iloc[:, 1:-1] 

    mean_scores = df.mean().round(2)
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
    st.markdown("""
    <style>
    .reportview-container .main .block-container {
        max-width: 100%;
    }
    .title {
        text-align: center;
        color: #4f8bf9;
        font-size: 50px;
        padding-top: 20px;
        padding-bottom: 20px;
    }
    .upload-container {
        margin-top: 30px;
        margin-bottom: 30px;
    }
    .button-container {
        margin-top: 30px;
    }
    .result-container {
        margin-top: 50px;
    }
    /* Add a gradient background to the table headers */
    table th {
        background: linear-gradient(to right, #4f8bf9, #202020);
        color: white;
    }
    /* Style for variable names in the table */
    .variable-names {
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>🎓 Student Grading System</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #4f8bf9;'>", unsafe_allow_html=True)
    cols = st.columns(5)
    School = cols[0].text_input("School Name")
    teacher_name = cols[1].text_input("Teacher's Name")
    Grade = cols[2].selectbox("Grade", options=['Select a Grade','PP1','PP2','Grade 1', 'Grade 2','Grade 3', 'Grade 4','Grade 5','Grade 6'])
    term = cols[3].selectbox("Term", options=['Select a term', 1, 2, 3])
    exam_type = cols[4].selectbox("Exam Type", options=['Select an exam type', 'Opening School', 'Midterm', 'End Term'])

    st.markdown("<div class='upload-container'>Please upload a CSV or Excel file with student grades:</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
        except Exception as e:
            data = pd.read_excel(uploaded_file)
        
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
            
        if 'NAMES' not in data.columns:
            st.error("File must contain a 'NAMES' column.")
            return
        
        st.markdown("<div class='result-container'>Data has been successfully uploaded.</div>", unsafe_allow_html=True)  

        if st.button('Calculate Grades 📊', key='calculate_button'):
            if not School or not teacher_name or not Grade or term == 'Select a term' or exam_type == 'Select an exam type':
               st.error("Please provide all the information.")
               return
        
            result = calculate_grades(data)
            main(result, School, teacher_name, Grade, term, exam_type)  
       
            col1, col2 = st.columns(2)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("## 📊 Mean Scores Plot", unsafe_allow_html=True)
                mean_scores_plot = create_mean_scores_plot(result)
                st.session_state['mean_scores_plot'] = mean_scores_plot
                st.pyplot(st.session_state['mean_scores_plot']) 

            
            with col2:
                st.markdown("## 📚 Mean Scores by Subject", unsafe_allow_html=True)
                mean_scores_table = create_mean_scores_table(result)
                st.session_state['mean_scores_table'] = mean_scores_table
                styled_mean_scores_table = mean_scores_table.rename(columns={
                    'Subject': "<span class='variable-names'>Subject</span>",
                    'Mean Score': "<span class='variable-names'>Mean Score</span>"
                }, inplace=False)
                st.write(styled_mean_scores_table.to_html(escape=False), unsafe_allow_html=True)
            
            row1, row2 = st.columns(2)
            row1.markdown(f"**School:** {School}")
            row1.markdown(f"**Teacher's Name:** {teacher_name}")
            row1.markdown(f"**Grade:** {Grade}")
            row2.markdown(f"**Term:** {term}")
            row2.markdown(f"**Exam Type:** {exam_type}")
            st.markdown("## 📝 Result Table", unsafe_allow_html=True)
            styled_result_table = result.rename(columns=lambda x: f"<span class='variable-names'>{x}</span>" if x in result.columns else x, inplace=False)
            st.write(styled_result_table.to_html(escape=False), unsafe_allow_html=True)
            if result is not None:
                st.session_state['result'] = result
                st.session_state['School'] = School
                st.session_state['Grade'] = Grade
                st.session_state['term'] = term
                st.session_state['exam_type'] = exam_type



            

def page2():
    st.markdown("""
    <style>
    .reportview-container .main .block-container {
        max-width: 100%;
    }
    .title {
        text-align: center;
        color: #4f8bf9;
        font-size: 50px;
        padding-top: 20px;
        padding-bottom: 20px;
    }
    .upload-container {
        margin-top: 30px;
        margin-bottom: 30px;
    }
    .button-container {
        margin-top: 30px;
    }
    .result-container {
        margin-top: 50px;
    }
    /* Add a gradient background to the table headers */
    table th {
        background: linear-gradient(to right, #4f8bf9, #202020);
        color: white;
    }
    /* Style for variable names in the table */
    .variable-names {
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>🔍 Detailed Student Report</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #4f8bf9;'>", unsafe_allow_html=True)

    if 'result' in st.session_state:
        result = st.session_state['result']

        selected_student = st.selectbox("Select student name:", result['NAMES'].unique())
        search_button = st.button("Generate Report 🔍")
        if search_button:
            student_data = result.query("NAMES == @selected_student")
            if not student_data.empty:
                st.markdown(f"""
    <div style="
        text-align: center;
        color: #4f8bf9;
        font-size: 30px;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 10px;
        margin: 10px;">
        Detailed Report for: {selected_student}
    </div>
    """, unsafe_allow_html=True)

                subjects = [col for col in student_data.columns if col != 'NAMES' and col != 'TOTAL MARKS']

                student_data.columns = student_data.columns.astype(str)

                student_scores = student_data[subjects].iloc[0]

                max_scores = result[subjects].max()
                difference_from_max = max_scores - student_scores
                difference_from_max = difference_from_max.rename("Difference from Max")

                ranks = student_scores.rank(ascending=False, method='min').astype(int)
                ranks = ranks.rename("Rank in Subject")

                st.write("<h3 style='color: #4f8bf9;'>Subject-wise Performance</h3>", unsafe_allow_html=True)
                styled_student_data = student_data.rename(columns=lambda x: f"<span class='variable-names'>{x}</span>" if x in subjects else x, inplace=False)
                st.write(styled_student_data.to_html(escape=False), unsafe_allow_html=True)

                student_rank = student_data.index[0]
                st.write(f"Rank: {student_rank}")

                student_scores = student_data[subjects].iloc[0]
                performance_comparison = student_scores.to_frame(name='Score')

                performance_comparison['Performance'] = ['Above Average' if score >= 70 else 'Average' if 50 <= score <= 69 else 'Below Average' for score in performance_comparison['Score']]

                performance_comparison['Needs Improvement'] = ['Yes' if score < 69  else 'No' for score in performance_comparison['Score']]

                st.write("<h3 style='color: #4f8bf9;'>Subject-wise Performance Summary</h3>", unsafe_allow_html=True)
                styled_performance_comparison = performance_comparison.rename(columns=lambda x: f"<span class='variable-names'>{x}</span>" if x in performance_comparison.columns else x, inplace=False)
                st.write(styled_performance_comparison.to_html(escape=False), unsafe_allow_html=True)

                st.write("<h3 style='color: #4f8bf9;'>Ranks in Each Subject and Difference from Highest Score</h3>", unsafe_allow_html=True)
                table2_data = pd.concat([ranks, difference_from_max], axis=1)
                styled_table2_data = table2_data.rename(columns=lambda x: f"<span class='variable-names'>{x}</span>" if x in ['Rank in Subject', 'Difference from Max'] else x, inplace=False)
                st.write(styled_table2_data.to_html(escape=False), unsafe_allow_html=True)

            else:
                st.write("Student not found.")
    else:
        st.write("No data available. Please calculate grades on the first page.")



def manual_page():
    st.title('📖 Application Manual')

    st.markdown("""
    <style>
    body {
        background-color: #202020;
    }
    h1 {
        color: #4f8bf9;
    }
    h2 {
        color: #df691a;
    }
    p {
        color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    # 📖 Student Grading System Application Manual

    ## Overview
    This application is designed to analyze student grades. It consists of two main pages: `Student Grade Calculator` and `Student Performance Analysis`.

    ## Page 1: Student Grade Calculator
    
    1. **Personal Information**: The teacher is required to provide his/her name, the class he/she teaches, Term, and exam type.

    2. **Upload a File**: The application accepts CSV or Excel files containing student grades. The file must contain a column named 'NAMES'. To upload a file, click on the "Choose a file" button and select the desired file from your device.

    3. **Calculate Grades**: After successfully uploading a file, click on the 'Calculate Grades' button. The application will calculate the total marks for each student and rank them accordingly.

    4. **Mean Scores Plot**: This plot visualizes the mean scores of all subjects. It helps to understand the overall performance of the students in each subject.

    5. **Mean Scores by Subject**: This table displays the mean scores of all subjects in descending order.

    6. **Result Table**: This table displays the calculated total marks and ranks of all students.

    ## Page 2: Student Performance Analysis

    1. **Student Search and Filter**: You can select a student name from the dropdown menu and click on the 'Search' button. The application will display the selected student's scores in all subjects and their total marks.

    Please note that the 'Student Performance Analysis' page requires data from the 'Student Grade Calculator' page. If no data is available, you will be prompted to calculate grades on the first page.

    ## General Usage Notes

    - The application uses a dark theme for better visibility. The text color is white and the background color is blue.

    - The sidebar contains a radio button for navigating between the three pages.

    - The application is designed to hide the sidebar and the Streamlit menu after a few seconds of inactivity.

    - The application layout is set to 'wide' for better utilization of screen space.

    This manual should help you navigate and use the application effectively.
    """, unsafe_allow_html=True)


def hide_sidebar():
    if st.sidebar:
        time.sleep(3) 
        st.sidebar.empty() 


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import toml
import secrets


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1dSlooUVS_hgm1C1xUyZ90kcYL7ZdMq0d-nKWrbz30Ls'


def load_secrets():
    try:
        with open("secrets.toml", "r") as file:
            secrets_data = toml.load(file)
            web_secrets = secrets_data.get('web', {})
            client_id = web_secrets.get('client_id')
            client_secret = web_secrets.get('client_secret')
            refresh_token = web_secrets.get('refresh_token')
            return client_id, client_secret, refresh_token
    except FileNotFoundError:
        logger.error("secrets.toml file not found.")
        return None, None, None



def get_google_sheet(credentials):
    try:
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        logger.info("Connected to Google Sheet")
        return sheet
    except Exception as e:
        logger.exception("Error while connecting to Google Sheet")
        return None


def save_result_to_google_sheet(result, School, Grade, term, exam_type, credentials):
    sheet = get_google_sheet(credentials)
    if sheet:
        try:
            table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_").lower()
            logger.info(f"Table name: {table_name}")
            header = result.columns.tolist()
            data = [header] + result.values.tolist()
            service = build("sheets", "v4", credentials=credentials)
            service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range=table_name).execute()
            service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=table_name, valueInputOption="USER_ENTERED", body={"values": data}).execute()
            logger.info("Data saved to Google Sheet")
        except Exception as e:
            logger.exception("Error while saving data to Google Sheet")
    else:
        logger.error("Failed to save data to Google Sheet. Connection failed.")



def main(result, School, teacher_name, Grade, term, exam_type):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        client_id, client_secret, refresh_token = load_secrets()
        if not client_id or not client_secret or not refresh_token:
            logger.error("Failed to load secrets data.")
            return 
        
        creds = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )

        if result is not None:
            save_result_to_google_sheet(result, School, Grade, term, exam_type, creds)
            st.session_state['result'] = result
            st.session_state['School'] = School
            st.session_state['Grade'] = Grade
            st.session_state['term'] = term
            st.session_state['exam_type'] = exam_type
            
    except Exception as e:
        logger.exception("Error during main execution")





pages = {
    "Student Grade Calculator": page1,
    "Student Performance Analysis": page2,
    "Manual": manual_page,
}

selected_page = st.sidebar.radio("Select your page:", tuple(pages.keys()))

pages[selected_page]()



