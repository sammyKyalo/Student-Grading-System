import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CREDENTIALS_FILE = 'client_secret_924931594615-37sd840ffcnbd300lmlskh5bpp3q62k9.apps.googleusercontent.com.json'
SHEET_NAME = 'results'

def get_google_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open(SHEET_NAME).sheet1 
        logger.info("Connected to Google Sheet")
        return sheet
    except Exception as e:
        logger.error("Error while connecting to Google Sheet: %s", e)
        return None

def save_result_to_google_sheet(result, School, Grade, term, exam_type):
    sheet = get_google_sheet()
    if sheet:
        try:
            table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_").lower()
            header = result.columns.tolist()
            data = [header] + result.values.tolist()
            sheet.clear()
            sheet.append_row(header)
            sheet.append_rows(data[1:])
            logger.info("Data saved to Google Sheet")
        except Exception as e:
            logger.error("Error while saving data to Google Sheet: %s", e)
    else:
        logger.error("Failed to save data to Google Sheet. Connection failed.")
