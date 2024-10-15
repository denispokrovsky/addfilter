import streamlit as st
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Set up Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_creds_from_secrets():
    creds_dict = dict(st.secrets["google_credentials"])
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return creds

def upload_to_drive(file):
    creds = get_creds_from_secrets()
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {'name': file.name}
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype=file.type, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

st.title('Google Drive File Uploader')

uploaded_file = st.file_uploader("Choose a file to upload to Google Drive", type=None)  # Allow any file type

if uploaded_file is not None:
    if st.button('Upload to Google Drive'):
        with st.spinner('Uploading file to Google Drive...'):
            try:
                file_id = upload_to_drive(uploaded_file)
                st.success(f"File uploaded successfully! File ID: {file_id}")
                st.info("You can use this File ID to access or share the file in Google Drive.")
            except Exception as e:
                st.error(f"An error occurred during upload: {str(e)}")
                st.exception(e)  # This will print out the full traceback

st.markdown("---")
st.write("Note: This app uses secure credentials stored in Streamlit secrets.")