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
    
    file_path = os.path.join(upload_dir, file_upload.name)
    with open(file_path, "wb") as f:
        f.write(buffer)

    return file_path

def generate_csv_file(pdf_file_path: str): 
    return asyncio.run(process_file_async(pdf_file_path))

def generate_flashcard_file(csv_file_path: str): 
    return process_file(csv_file_path)

st.title("Flashcard Generator")

# Upload section 
file_upload = st.file_uploader("Choose CSV/PDF file", type=["pdf", "csv"], accept_multiple_files=False)
uploaded_file_path = None

if file_upload is not None:
    try: 
        uploaded_file_path = save_uploaded_file(file_upload.name, file_upload.getbuffer())
    except Exception as e:
        st.error(f"An error occurred: {e}")

is_pdf_upload = uploaded_file_path is not None and uploaded_file_path.endswith(".pdf")
is_csv_upload = uploaded_file_path is not None and uploaded_file_path.endswith(".csv")

csv_file_path = uploaded_file_path if is_csv_upload else None
pdf_file_path = uploaded_file_path if is_pdf_upload else None
txt_file_path = None

if is_pdf_upload:
    # Generate CSV section
    st.header("1. Generate CSV file")
    st.write(f"Generate CSV file from PDF \"{uploaded_file_path}\"")

    skip_translation = st.checkbox("Skip translation", value=False)
    skip_segmentation = st.checkbox("Skip segmentation", value=False)

    ChinesePhrase.SKIP_TRANSLATION = skip_translation
    ChinesePhrase.SKIP_SEGMENTATION = skip_segmentation

    if st.button("Convert"):
        try:
            csv_file_path = generate_csv_file(uploaded_file_path)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            raise 

if is_csv_upload:
    # Generate Flashcards section
    st.header("Generate Flashcards")

if is_pdf_upload and csv_file_path is not None:
    # Generate Flashcards section
    st.header("2. Generate Flashcards")

if csv_file_path is not None:
    st.write(f"Generate flashcards from CSV {csv_file_path}...")

    translation_template = st.text_area("Flashcared Template", value="{translation}")
    translation_template = translation_template.strip().replace("\\n", "\n").replace("\\t", "\t") + "\n"
    skip_segmented = st.checkbox("Skip segmented", value=False)
    FlashcardGenerator.TEMPLATE = translation_template

    if st.button("Generate Flashcards"):
        try: 
            txt_file_path = generate_flashcard_file(csv_file_path)
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