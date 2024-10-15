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
        return True
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return False

st.title('Предпроцессинг анализа текстового содержания')

drive_service = get_drive_service()
share_email = st.secrets.get("share_email")

uploaded_file = st.file_uploader("Выбираем файл для анализа текстового содержания", type=None)

if uploaded_file is not None:
    if st.button('Передатть в обработку'):
        with st.spinner('Приступаю...'):
            try:
                file_id = upload_to_drive(drive_service, uploaded_file)
                st.success(f"Успешно! Код операции: {file_id}")
                
                if share_email:
                    if share_file(drive_service, file_id, share_email):
                        st.success(f"Анализ сделан, ждите загрузки")
                        #file_link = f"https://drive.google.com/file/d/{file_id}/view"
                        #st.markdown(f"You can access the file [here]({file_link})")
                        #st.info("If you can't access the file immediately, please check your email for the sharing notification from Google Drive.")
                else:
                    st.warning("File was uploaded but not processed")
            except Exception as e:
                st.error(f"An error occurred during...: {str(e)}")
                st.exception(e)  # This will print out the full traceback

st.markdown("---")
st.write("Скоро файл будет обработан")