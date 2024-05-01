import streamlit as st


# def clear_page():
#     if st.session_state['method'] == "Youtube":
#         #want to clear the 'method of upload' and link and submit button
#         st.session_state.pop('link', None)
#         st.session_state.pop('submit', None)
#         st.success("Link successfully retrieved")
#     elif st.session_state['method'] == "Manual Upload":
#         #want to clear the method of upload and file upload and upload button
#         st.session_state.pop('file', None)
#         st.session_state.pop('upload_button', None)
#         st.success("File successfuly uploaded")

def run_app():

    if st.session_state['method'] == "Youtube":
        # st.session_state.success_message = "File successfully retrieved!"
        st.session_state['method'] = st.write("")
        st.session_state['link'] = st.write("")
        st.session_state['submit'] = st.write("")
        st.success("File successfully retrieved!")

    else:
        st.success("File successfully uploaded!")
        # st.session_state.success_message = "File successfully uploaded!"

# Banner and Initial Options
st.image(r"streamlit/notesmaxx_banner.png", use_column_width=True)
st.markdown("<br>", unsafe_allow_html=True)
method_of_upload = st.selectbox("Select your preferred upload method: ", options=["Youtube", "Manual Upload"],
                                key="method")

# Process Upload Method Selection
if method_of_upload == "Youtube":
    youtube_link = st.text_input("Please provide link to the Youtube video: ", key="link")
    col1, col2, col3 = st.columns([1, 0.3, 1])
    submit_btn = col2.button("SUBMIT", on_click=run_app, key="submit")  # Button now calls clear_page()

else:
    file_upload = st.file_uploader("Please Upload Manually: ", type=["mp4", "mkv", "flv", "webm"], key="file")
    col1, col2, col3 = st.columns([1, 0.4, 1])
    upload_btn = col2.button("UPLOAD", on_click=run_app, key="upload_button")

st.markdown("<br>", unsafe_allow_html=True)
# # Placeholder for success message
# if 'success_message' in st.session_state:
#     st.success(st.session_state.success_message)
#     st.rerun()
#     del st.session_state['success_message']


st.image(r"streamlit/clean_banner.jpg", use_column_width=True)
