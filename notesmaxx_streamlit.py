import firebase_admin

import streamlit as st
from notesmaxx_transcribe_logic import run_notesmaxx
from firebase_admin import credentials
import os
from moviepy.editor import VideoFileClip
import tempfile
from firebase_admin import credentials, db

# setting up firebase
# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("notesmaxx-1e894-firebase-adminsdk-4voc1-c1498225a3.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://notesmaxx-1e894-default-rtdb.firebaseio.com/'
    })
ref = db.reference('user_name_email_review')

st.image(r"streamlit/notesmaxx_banner.png", use_column_width=True)
# Add empty space to create a gap
st.markdown("<br>", unsafe_allow_html=True)
st.sidebar.title("Welcome To The App!")


def reset_session_state():
    st.session_state['method_of_upload'] = None
    st.session_state['link'] = ""
    st.session_state['file_upload'] = None
    st.session_state['submit_btn'] = False
    st.session_state['upload_btn'] = False
    st.session_state['full_text'] = ""
    st.session_state['image'] = None


def save_user_data(name=None, email=None, review=None):
    if name is None and email is None and review is None:
        return  # No data provided, do nothing

    user_data = {
        'name': name if name is not None else "Not found",
        'email': email if email is not None else "Not found",
        'review': review if review is not None else "Not found"
    }
    ref.push(user_data)
    st.session_state['user_name'] = ""
    st.session_state['user_email'] = ""
    st.session_state['user_review'] = ""
    st.session_state['extra'] = ""
    st.sidebar.success("Feedback appreciated!")


def get_user_info():
    # with st.sidebar.form(key='user_feedback_form'):
    #     st.write("Please provide your name and email:")
    #     name = st.text_input("Name", key="user_name")
    #     email = st.text_input("Email", key="user_email")
    #     review = st.text_area("Review or suggestions highly appreciated:", key="user_review")
    #     submit_user_data = st.form_submit_button("ENTER", on_click=save_user_data, args=[name, email, review,])


    st.sidebar.write("Please provide your name and email:")

    name = st.sidebar.text_input("Name", key="user_name")
    email = st.sidebar.text_input("Email", key="user_email")
    review = st.sidebar.text_area("\nReview or suggestions highly appreciated!", key="user_review")
    st.sidebar.text_input("Anything else?", key="extra")
    submit_user_data = st.sidebar.button("ENTER", on_click=lambda: save_user_data(name, email, review,))


if __name__ == "__main__":
    st.sidebar.title("App Controls")
    button_placeholder = st.sidebar.empty()
    get_user_info()
    if button_placeholder.button("Reset"):
        reset_session_state()

# use session state
if 'method_of_upload' not in st.session_state or 'link' not in st.session_state or 'file_upload' not in st.session_state or 'submit_btn' not in st.session_state or 'upload_btn' not in st.session_state:
    st.session_state['method_of_upload'] = None
    st.session_state['link'] = ""
    st.session_state['file_upload'] = None
    st.session_state['submit_btn'] = False
    st.session_state['upload_btn'] = False
    st.session_state['image'] = None

method_of_upload = st.selectbox("Select your preferred upload method: ", options=["Youtube", "Manual Upload"],
                                key="method_of_upload")

if st.session_state['method_of_upload'] != method_of_upload:
    st.session_state['method_of_upload'] = method_of_upload

new_variable = "hello"


def run_app():
    # Clear previous content
    placeholder = st.empty()
    if st.session_state['method_of_upload'] == "Youtube":
        link_check = st.session_state['link']
        if len(link.strip()) > 0 and "youtube.com" in link:
            text, image = run_notesmaxx(st.session_state['method_of_upload'], st.session_state['link'])
            st.session_state['full_text'] = text
            st.session_state['image'] = image
        else:
            st.warning("Please enter a valid youtube link!")
    else:
        # Read the uploaded file
        if st.session_state['file_upload'] is not None:
            file_contents = st.session_state['file_upload'].read()
            # Create a temporary file to store the uploaded video
            temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            # Write the uploaded video file contents to the temporary file
            temp_video_file.write(file_contents)
            # Close the temporary video file
            temp_video_file.close()

            # Create a temporary file to store the extracted audio
            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')

            try:
                # Extract audio from the video file and save it as WAV
                video = VideoFileClip(temp_video_file.name)
                audio = video.audio
                audio.write_audiofile(temp_audio_file.name)
                audio.close()
                video.close()

                # Get the path of the temporary audio file
                temp_audio_file_path = temp_audio_file.name

                # Pass the path of the temporary audio file to run_notesmaxx
                text, image = run_notesmaxx(st.session_state['method_of_upload'], temp_audio_file_path)
                # Store the processed text and image
                st.session_state['full_text'] = text
                st.session_state['image'] = image

            finally:
                # Close and remove temporary files
                temp_video_file.close()
                temp_audio_file.close()
                os.unlink(temp_video_file.name)
                os.unlink(temp_audio_file.name)
        else:
            st.warning("Please upload a file!")
    # else:
    #      # Read the uploaded file
    #      if st.session_state['file_upload'] is not None:
    #         file_contents = st.session_state['file_upload'].read()
    #         # Create a temporary file
    #         temp_file = tempfile.NamedTemporaryFile(delete=False)
    #         # Write the uploaded file contents to the temporary file
    #         temp_file.write(file_contents)
    #         # Get the path of the temporary file
    #         temp_file_path = temp_file.name
    #         text, image = run_notesmaxx(st.session_state['method_of_upload'], temp_file_path)
    #         temp_file.close()
    #         st.session_state['full_text'] = text
    #         st.session_state['image'] = image


if st.session_state['method_of_upload'] == "Youtube":
    link = st.text_input("Please provide link to the Youtube video: ", key="link")
    col1, col2, col3 = st.columns([1, 0.3, 1])
    submit_btn = col2.button("SUBMIT", on_click=run_app)


else:
    file_upload = st.file_uploader("Please Upload Manually: ", type=["mp4", "mkv", "flv", "webm"])
    if file_upload is not None:
        st.session_state['file_upload'] = file_upload
    col1, col2, col3 = st.columns([1, 0.4, 1])
    upload_button = col2.button("UPLOAD", on_click=run_app)

# Display full text at the bottom
col4, col5 = st.columns([1, 2])
placeholder_full_text = st.empty()
placeholder_image = st.empty()

with col4:
    if st.session_state['image'] is not None:
        placeholder_image.image(st.session_state['image'], use_column_width=True)
        st.success("Notes successfully generated!")
    else:
        st.warning("No notes have been created yet.")

# Define custom CSS style for the text
custom_css = """
<style>
    .styled-text {
        background-color: black;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-size: 23px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Use an elegant font */
        line-height: 1.6; /* Adjust line height for better readability */
        text-align: justify; /* Align text to justify for a cleaner look */
        text-justify: inter-word; /* Adjust text justification */
    }
</style>
"""
with col5:
    # Apply custom CSS style to the text
    placeholder_full_text.markdown(
        custom_css +
        f"<hr style='border: 2px solid #f0f0f0'><br>"
        f"<div class='styled-text'>"
        f"{st.session_state.get('full_text', '')}"
        f"</div>"
        f"<hr style='border: 2px solid #f0f0f0'><br>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)
st.image(r"streamlit/clean_banner.jpg", use_column_width=True)
