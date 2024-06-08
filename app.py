import streamlit as st
import boto3
import os

# Dictionary to store user credentials (username: password)
USER_CREDENTIALS = {
    "admin": "password",
    "user1": "user1password",
    "user2": "user2password"
}

# Function to check credentials
def check_credentials(username, password):
    return USER_CREDENTIALS.get(username) == password

# Authentication form
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = ""

if not st.session_state['authenticated']:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success("Login successful")
            st.experimental_rerun()  # Reload the app to reflect authentication status
        else:
            st.error("Invalid username or password")
else:
    aws_access_key_id = st.secrets['aws_access_key_id']
    aws_secret_access_key = st.secrets['aws_secret_access_key']
    bucket_name = st.secrets['bucket_name']

    # Initialize the S3 client
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    def list_folders(bucket_name):
        result = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
        folders = []

        if 'CommonPrefixes' in result:
            for prefix in result['CommonPrefixes']:
                folders.append(prefix['Prefix'])

        return folders

    def create_folder(bucket_name, folder_name):
        if not folder_name.endswith('/'):
            folder_name += '/'
        s3.put_object(Bucket=bucket_name, Key=folder_name)

    def upload_file(bucket_name, folder_name, file):
        file_name = os.path.basename(file.name)
        s3.upload_fileobj(file, bucket_name, f"{folder_name}{file_name}")

    # List folders
    folders = list_folders(bucket_name)

    # Sidebar select box
    sidebar_selectbox = st.sidebar.selectbox(
        "...",
        ("Upload Files", "Create Folder")
    )

    if sidebar_selectbox == "Create Folder":
        st.title("View and Create Folders")
        if st.button("View All Folders"):
            st.write(folders)
        st.write("\n\n\n")
        st.write("---")
        st.title("Create New Folder")
        folder_name = st.text_input("Enter the name of the folder")
        if st.button("Create Folder"):
            if folder_name:
                create_folder(bucket_name, folder_name)
                st.success(f"Folder '{folder_name}' created successfully")
            else:
                st.error("Please enter a folder name")

    if sidebar_selectbox == "Upload Files":
        st.title("Upload Files")
        if folders:
            folder_name = st.selectbox("Select Folder", folders)
            file = st.file_uploader("Choose a file")
            if st.button("Upload"):
                if folder_name and file:
                    upload_file(bucket_name, folder_name, file)
                    st.success(f"File '{file.name}' uploaded to '{folder_name}' successfully")
                else:
                    st.error("Please select a folder and choose a file to upload")
        else:
            st.warning("No folders available. Please create a folder first.")

    # Logout button
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = ""
        st.experimental_rerun()
