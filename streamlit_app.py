import streamlit as st
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import Flow
import json

# Set up Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_creds_from_secrets():
    creds_info = st.secrets["google_credentials"]
    creds = Credentials.from_authorized_user_info(info=json.loads(creds_info), scopes=SCOPES)
    return creds

def authenticate():
    creds = get_creds_from_secrets()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                st.error("Credentials have expired. Please contact the administrator to update the credentials.")
                st.stop()
        else:
            st.error("No valid credentials found. Please contact the administrator to set up the credentials.")
            st.stop()
    return creds

def upload_to_drive(file):
    creds = authenticate()
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

st.markdown("---")
st.write("Note: This app uses secure credentials stored in Streamlit secrets.")