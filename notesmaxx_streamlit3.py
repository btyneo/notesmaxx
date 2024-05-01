import streamlit as st


def run_app():
    if st.session_state['method'] == "Youtube":
        st.success("File successfully retrieved!")
    else:
        st.success("File successfully uploaded!")


# Banner and Initial Options
st.image(r"streamlit/notesmaxx_banner.png", use_column_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# Select method of upload #Process Upload Method Selection #ALL PLACEHOLDERS
method_placeholder = st.empty()

file_upload_placeholder = st.empty()
youtube_link_placeholder = st.empty()
upload_button_placeholder = st.empty()
submit_button_placeholder = st.empty()



method_of_upload = method_placeholder.selectbox("Select your preferred upload method: ",
                                                options=["Youtube", "Manual Upload"],
                                                key="method")

#
if method_of_upload == "Youtube":

    youtube_link = youtube_link_placeholder.text_input("Please provide link to the Youtube video: ", key="link")
    col1, col2, col3 = st.columns([1, 0.3, 1])

    submit_btn = submit_button_placeholder.button("SUBMIT", on_click=run_app, key="submit")

else:

    file_upload = file_upload_placeholder.file_uploader("Please Upload Manually: ",
                                                        type=["mp4", "mkv", "flv", "webm"],
                                                        key="file")
    col1, col2, col3 = st.columns([1, 0.4, 1])

    upload_btn = upload_button_placeholder.button("UPLOAD", on_click=run_app, key="upload_button")

st.markdown("<br>", unsafe_allow_html=True)
st.image(r"streamlit/clean_banner.jpg", use_column_width=True)
