import whisper
import langchain
import yt_dlp
import tempfile  # we will use this for the free version//file is deleted after using
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains.summarize import load_summarize_chain
import textwrap
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
import uuid
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import re
import gdown
from notesmaxx_generate_image import create_image

# setting up google drive: loading credentials, creating drive service object, uploading
credentials = service_account.Credentials.from_service_account_file(
    r"C:\Users\hamza\PycharmProjects\notesmaxx\notesmaxxaudios-57d6b09c8d15.json")
# Create a Drive service object
drive_service = build('drive', 'v3', credentials=credentials)
paid = False
# while True:
#     paid_or_not = input("Paid Or Not: ")
#     if paid_or_not.lower() in ['yes', 'y', 'true']:
#         paid = True
#         break
#     elif paid_or_not.lower() in ['no', 'n', 'false']:
#         paid = False
#         break
#     else:
#         print("Error! 'Yes' Or 'No' only!")

is_meeting = True
model = whisper.load_model('base')
load_dotenv()


# final summary list

def upload_to_google_drive(path):
    random_filename = str(uuid.uuid4())
    response = drive_service.files().get(fileId='root', fields='id').execute()
    root_folder_id = response.get('id')
    file_metadata = {'name': f"{random_filename}",
                     'parents': [root_folder_id]}  # this is the filename itll have in google drive
    media = MediaFileUpload(f"{path}",
                            mimetype='audio/mpeg')  # Update with your file's MIME type #this is current path of file
    drive_service.files().create(body=file_metadata, media_body=media).execute()
    print("uploaded to drive")


def extract_audio_local(path):
    # random_filename = str(uuid.uuid4())
    # path = input("Enter file path: ")
    text_local = model.transcribe(path)
    # if paid:
    #     upload_to_google_drive(path)
    return text_local


# def extract_audio_from_google_drive():
#     random_filename = str(uuid.uuid4())
#     drive_url = input("Enter Google Drive URL: ")
#     #we need to extract the id from the url
#     video_id = drive_url.split("/")[-2] #like it will be https://drive.google.com/file/d/1ihCR2ymI1ja0EhTu__Mq_QGfGpqfoO8D/view?usp=sharing
#     download_url = f"https://drive.google.com/uc?id={video_id}"
#     print(video_id)
#     print(download_url)
#     path = fr"savedaudios2/{random_filename}.mp3"
#     gdown.download(download_url, path, quiet=False)
#     transcription = whisper.transcribe(fr"savedaudios2/{random_filename}.mp3")
#     return transcription


def extract_audio_from_youtube(streamlit_url):
    # setting the whisper model
    random_filename = str(uuid.uuid4())
    # set the downloading options (from youtube) to only audio/best quality audio
    yt_options = {'quiet': True,  # wont show in terminal when its downloading
                  'format': 'bestaudio/best',
                  'postprocessors': [{
                      'key': 'FFmpegExtractAudio',  # extracting audio from the video
                      'preferredcodec': 'mp3'
                  }],
                  'outtmpl': f'savedaudios/{random_filename}'
                  }

    # url = input("Enter youtube video URL: ")
    url = streamlit_url
    with yt_dlp.YoutubeDL(yt_options) as yt_audio:
        info = yt_audio.extract_info(url, download=False)
        video_title = info.get('title', None)  # Extract video title from metadata
        yt_audio.download(url_list=[url])
        audio_path = os.path.abspath(fr"savedaudios/{random_filename}.mp3")
        # remember that whisper.transcribe requires the absoloute path, not the relative one so use .abspath

    # now transcribe the audio using whisper
    vid_text = model.transcribe(audio_path)
    if paid:
        upload_to_google_drive(audio_path)
    return vid_text


def truncate_prompt(prompt, max_tokens=4096, max_chars=4000):
    # Tokenize the prompt
    tokens = prompt.split()

    # Check if the token count exceeds the limit or if the character count is too high
    if len(tokens) > max_tokens or len(prompt) > max_chars:
        # Truncate the prompt to the specified token and character limits
        truncated_tokens = tokens[:max_tokens]
        extra_tokens = tokens[max_tokens::]
        extra_chars = ' '.join(extra_tokens)
        truncated_chars = ' '.join(truncated_tokens)[:max_chars]

        return [truncated_chars, extra_chars]
    else:
        return prompt


def summarize_text(text_from_vid, is_meeting):
    # now that we have our text from the video we come outside of the with tempfile statement which means temp file is deleted
    # now use langchain to get a summary. first prepare a proper prompt

    # prepare 2 prompts, 1 for if its a meeting, and 1 for if its a class lecture

    llm = OpenAI(temperature=0)
    meeting_prompt = """ You will receive a transcript from a workplace's online meeting. You need to pick out main points and
    summarize them and output them. The points need to be organized in bullet points. Make it clear and concise. Make sure its a detailed summary. 
    Make it work environment friendly. Make sure each bullet point is seperated by a new line and starts with '-'\n.
    Be specific with the summary. Keep it concise and to the point. No irrelevant details. 
    If there are any things that we need to do or any tasks that are assigned, add them as a [TO DO LIST:] at the end of the summary.
    

    
    
    Transcript: {text}
    
    Summary: \n
    
    """

    lesson_prompt = """ You will receive a transcript from a student's online class recording. You need to pick out main points and
    summarize them and output them. The points need to be organized in bullet points. Make it clear and concise. Make sure its a detailed summary. 
    Make it student friendly. Make sure each bullet point is seperated by a new line and starts with '-'\n.
    Be specific with the summary. Keep it concise and to the point. No irrelevant details. 
    If there are any things that we need to do or any tasks that are assigned, add them as a [TO DO LIST:] at the end of the summary.
  
    
    Transcript: {text}
    
    Summary:\n
    
  
    """

    prompt_meeting = PromptTemplate(llm=llm, template=meeting_prompt, input_variables=["text"])
    prompt_lesson = PromptTemplate(llm=llm, template=lesson_prompt, input_variables=["text"])
    if is_meeting:
        prompt_current_raw = meeting_prompt
        current_prompt = prompt_meeting
    else:
        prompt_current_raw = lesson_prompt
        current_prompt = prompt_lesson

    compressed_text = truncate_prompt(text_from_vid)
    text_from_vid = compressed_text[0]
    extra_text = compressed_text[1]

    prompt_final = PromptTemplate(llm=llm, template=prompt_current_raw, input_variables=["text"])

    chain = load_summarize_chain(llm=llm, chain_type="stuff", prompt=prompt_final)

    def text_summary_final(text):

        # splitting the text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50, separators=[" ", ",", "\n"])
        split_text = text_splitter.split_text(text)

        docs = []
        docs = [Document(page_content=t) for t in split_text]
        summary_final = chain.run(docs)
        wrapped_text = textwrap.fill(summary_final, width=1000, break_long_words=True, replace_whitespace=True)
        return wrapped_text

    final_summary.append(text_summary_final(text_from_vid))
    if extra_text:
        while extra_text:
            if len(extra_text) <= 4000:
                final_summary.append(text_summary_final(extra_text))
                break
            else:
                chunk = extra_text[:4000]
                final_summary.append(text_summary_final(chunk))
                extra_text = extra_text[4000:]


# #
# text = extract_audio_from_youtube()
# text = extract_audio_from_google_drive()
# text = extract_audio_local()
# yt_or_local = input("Youtube Link (1) Or Manual Upload (2): ")
# while yt_or_local not in ['1', '2']:
#     yt_or_local = input("Please Enter 1 or 2 Only!\nYoutube Link (1) Or Manual Upload (2): ")

# if yt_or_local == '1':
#     text = extract_audio_from_youtube()
# elif yt_or_local == '2':
#     text = extract_audio_local()
final_summary = []


def run_notesmaxx(yt_or_manual, video_file):
    if yt_or_manual == "Youtube":
        text = extract_audio_from_youtube(video_file)
    elif yt_or_manual == "Manual Upload":
        text = extract_audio_local(video_file)  # edit thisto update path


    summarize_text(text['text'], is_meeting)
    formatted_summary_final = final_summary[-1].split('-\n')
    todolist_exists = False
    format_for_notes = []

    for y, text2 in enumerate(final_summary):
        formatted = text2.split(' - ')
        if '[TO DO LIST:]' in text2:
            to_do_list = text2.split('[TO DO LIST:]')
            todolist_exists = True
        for x in formatted:
            if "[TO DO LIST:]" in x:
                break
            if x.strip() != "" and x.strip() != " ":
                format_for_notes.append(x.strip())
            x = x.strip()

        formatted = '. '.join(formatted[1::])
        formatted = formatted.split('[TO DO LIST:]')
        formatted = formatted[0]
        image = create_image(format_for_notes)
        return formatted, image
    #     print(
    #         f"\n{formatted}")  # 'formatted' is the paragraph. format_for_notes is the list which has this paragraph in points. to_do_list is self explanatory.
    #
    # print(f"\n")
    # for x, y in enumerate(format_for_notes):
    #     if x != 0:
    #         if x != len(format_for_notes):
    #             print(f"• {y}")

    # if todolist_exists:
    #     print(f"\n{to_do_list[1]}")

