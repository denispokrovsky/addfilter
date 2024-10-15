import streamlit as st
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Set up Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

@st.cache_resource
def get_drive_service():
    creds_dict = dict(st.secrets["google_credentials"])
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_to_drive(service, file):
    file_metadata = {'name': file.name}
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype=file.type, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def share_file(service, file_id, email):
    try:
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        st.success(f"File shared with {email}")
    except Exception as e:
        st.error(f"An error occurred while sharing the file: {str(e)}")

st.title('Google Drive File Uploader and Sharer')

drive_service = get_drive_service()
share_email = st.secrets.get("share_email")

uploaded_file = st.file_uploader("Choose a file to upload to Google Drive", type=None)

if uploaded_file is not None:
    if st.button('Upload to Google Drive'):
        with st.spinner('Uploading file to Google Drive...'):
            try:
                file_id = upload_to_drive(drive_service, uploaded_file)
                st.success(f"File uploaded successfully! File ID: {file_id}")
                st.info("You can use this File ID to access or share the file in Google Drive.")
                
                if share_email:
                    if st.button('Share File'):
                        share_file(drive_service, file_id, share_email)
                else:
                    st.warning("No share email configured in secrets. File was uploaded but not shared.")
            except Exception as e:
                st.error(f"An error occurred during upload: {str(e)}")
                st.exception(e)  # This will print out the full traceback

st.markdown("---")
st.write("Note: This app uses secure credentials stored in Streamlit secrets.")