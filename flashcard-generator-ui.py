import streamlit as st 
import os
from extract_chinese_from_pdfs import ChinesePhrase, process_file_async 
from generate_flashcards_from_csvs import FlashcardGenerator, process_file
import pyperclip
import asyncio

upload_dir = ".\\uploaded"

def save_uploaded_file(file_path: str, buffer): 
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(buffer)

    return file_path

st.title("Flashcard Generator")

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])
uploaded_file_path = None

if uploaded_file is not None:
    uploaded_file_path = save_uploaded_file(uploaded_file.name, uploaded_file.getbuffer())
    st.success(f"PDF saved to {uploaded_file_path}")

    csv_file_path = None
    try: 
        ChinesePhrase.SKIP_TRANSLATION = True
        ChinesePhrase.SKIP_SEGMENTATION = True
        csv_file_path = asyncio.run(process_file_async(uploaded_file_path))
        st.success(f"CSV file saved to {csv_file_path}")
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        raise

    txt_file_path = None
    try: 
        FlashcardGenerator.TEMPLATE = "{text}\t{text} ({pinyin})\n"
        txt_file_path = process_file(csv_file_path)
        st.success(f"TXT file saved to {txt_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        raise

    if txt_file_path is not None:
        with open(txt_file_path, "r", encoding="utf-8") as file:
            txt_content = file.read()
        st.text_area("Generated Flashcards", txt_content, height=300)
        
        if st.button("Copy to Clipboard"):
            pyperclip.copy(txt_content)
            st.success("Flashcards copied to clipboard")

