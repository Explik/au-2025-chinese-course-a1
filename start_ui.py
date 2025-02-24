import platform
import streamlit as st 
from streamlit import session_state
import os
from extract_chinese_from_pdfs import ChinesePhrase, process_file_async 
from generate_flashcards_from_csvs import FlashcardGenerator, process_file
import asyncio
import json

upload_dir = ".\\uploads"

environment_value = os.getenv("ENVIRONMENT", "local")
is_local = environment_value == "local"

print("Running in environment: ", environment_value)

# (State) functions
def save_uploaded_file(file_name: str, buffer): 
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(buffer)

    return file_path

def reveal_file_in_explorer(file_path: str):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS or Linux
            if sys.platform == 'darwin':  # macOS
                subprocess.call(['open', '-R', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
    except Exception as e:
        st.error(f"An error occurred while trying to reveal the file: {e}")

def create_copy_button(st, text, text_content):
    # Fetch copy button template
    html_template_file_path = os.path.join(".", "copy-button.html")
    with open(html_template_file_path, 'r') as file:
        html_template = file.read()

    # Create copy button from template and txt content
    html = html_template \
        .replace("BUTTON_TEXT", text) \
        .replace("TEXT_CONTENT", json.dumps(text_content))
    
    st.components.v1.html(html, height=40)

def get_mode(): 
    if session_state.get("mode", None) is not None: 
        return session_state.mode

    return None

def get_pdf_path(): 
    if session_state.get("pdf_file_path", None) is not None:
        return session_state.pdf_file_path
    
    return None

def get_csv_path():
    csv_process = session_state.get("csv_process", None)
    if csv_process is None: 
        return None 
    
    csv_process_status = csv_process.get("status", None)
    if csv_process_status != "completed":
        return None
    
    return csv_process.get("result")

def get_txt_path(): 
    txt_process = session_state.get("txt_process", None)
    if txt_process is None:
        return None
    
    txt_process_status = txt_process.get("status", None)
    if txt_process_status != "completed":
        return None
    
    return txt_process.get("result")

def get_txt_content(): 
    txt_file_path = get_txt_path()
    if txt_file_path is None:
        return None
    
    with open(txt_file_path, "r", encoding="utf-8") as file:
        return file.read()

def get_csv_content():
    csv_file_path = get_csv_path()
    if csv_file_path is None:
        return None
    
    with open(csv_file_path, "r", encoding="utf-8") as file:
        return file.read()

# Callbacks 
def handle_file_upload():
    file_upload = session_state.get("file_upload", None)
    if file_upload is None:
        print("Warning, No file uploaded")
        return 

    try: 
        file_name = file_upload.name
        uploaded_file_path = save_uploaded_file(file_name, file_upload.getbuffer())

        if (file_name.endswith(".pdf")):
            session_state.mode = "pdf"
            session_state.pdf_file_path = uploaded_file_path
            session_state.csv_process = None
            session_state.txt_process = None
            return
        if (file_name.endswith(".csv")):
            session_state.mode = "csv"
            session_state.pdf_file_path = None
            session_state.csv_process = {
                "status": "completed",
                "result": uploaded_file_path
            }
            session_state.txt_process = None
            return
        
        st.error("Invalid file format. Please upload a PDF or CSV file.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

def handle_pdf_convert(): 
    pdf_file_path = get_pdf_path()
    skip_translation = session_state.get("skip_translation")
    skip_segmentation = session_state.get("skip_segmentation")

    if pdf_file_path is None:
        st.error("No PDF file uploaded")
        return

    try: 
        session_state.csv_process = {
            "status": "started",
        }
        session_state.txt_process = None
        st.spinner("Processing...") 
        
        ChinesePhrase.SKIP_TRANSLATION = skip_translation
        ChinesePhrase.SKIP_SEGMENTATION = skip_segmentation
        csv_file_path = asyncio.run(process_file_async(pdf_file_path, os.path.join(".", "uploads-output")))

        session_state.csv_process = {
            "status": "completed",
            "result": csv_file_path
        }
    except Exception as e:
        st.error(f"An error occurred: {e}")

        session_state.csv_process = {
            "status": "failed",
            "error": str(e)
        }

def handle_csv_convert(): 
    csv_file_path = get_csv_path()

    if csv_file_path is None:
        st.error("No CSV file uploaded")
        return
    
    try: 
        session_state.txt_process = {
            "status": "started",
        }
        st.spinner("Processing...")

        raw_template = session_state.get("translation_template")
        template = raw_template.strip().replace("\\n", "\n").replace("\\t", "\t") + "\n"
        FlashcardGenerator.TEMPLATE = template
        
        skip_segmented = session_state.get("skip_segmented", False)
        FlashcardGenerator.SKIP_SEGMENTED = skip_segmented

        flashcard_file_path = process_file(csv_file_path)

        session_state.txt_process = {
            "status": "completed",
            "result": flashcard_file_path
        }
    except Exception as e:  
        st.error(f"An error occurred: {e}")

        session_state.txt_process = {
            "status": "failed",
            "error": str(e)
        }

# Setting up application state 
mode = get_mode()
pdf_file_path = get_pdf_path()
csv_file_path = get_csv_path()
txt_file_path = get_txt_path()

# Debugging
#print("=====================================")
#print(f"Mode: {mode}")
#print(f"PDF: {pdf_file_path}")
#print(f"CSV: {csv_file_path}")
#print(f"TXT: {txt_file_path}")
#print(f"Session State: {session_state}")

# Upload section 
st.title("CH-DA Flashcard Generator")
st.write("Upload a PDF or an already generated CSV file to generate flashcards.")

file_upload = st.file_uploader(
    "Choose CSV/PDF file", 
    key="file_upload",
    type=["pdf", "csv"], 
    accept_multiple_files=False,
    on_change=handle_file_upload)

# Generate CSV section
if mode == "pdf":
    st.header("1. Generate CSV file")
    st.write(f"Generate CSV file from PDF (with location \"{pdf_file_path}\")")

    skip_segmentation = st.checkbox("Skip segmentation", key="skip_segmentation", value=True)
    skip_translation = st.checkbox("Skip translation", key="skip_translation", value=False)

    st.button(
        "Convert", 
        on_click=handle_pdf_convert)
    
    if csv_file_path is not None: 
        col1, col2 = st.columns([6, 2])
        with col1:
            st.success(f"CSV file generated: {csv_file_path}")
        with col2:
            if is_local: 
                st.button(
                    "Open file",
                    key="open_csv_file",
                    use_container_width=True,
                    on_click=lambda: reveal_file_in_explorer(csv_file_path))
            else: 
                st.download_button(
                    "Download file",
                    get_csv_content(),
                    "flashcards.csv",
                    key="download_csv_file")

# Generate Flashcards section
if csv_file_path is not None:
    if mode == "pdf":
        st.header("2. Generate Flashcards")
    if mode == "csv":
        st.header("Generate Flashcards")

    st.text(f"Generate flashcards from CSV (with location \"{csv_file_path}\").")
    st.text(""\
            "The following template will be used to generate flashcards pr. row in the CSV. " \
            "The template allows for the following placeholders and special characters:\n" \
            "- {text} - The Chinese text\n" \
            "- {pinyin} - The Pinyin pronunciation\n" \
            "- {translation} - The translation\n" \
            "- \\t - Tab character\n" \
            "- \\n - New line character\n" \
            "".strip())
    
    st.text_area("Flashcared Template", value="{text} ({pinyin})\\t{translation}", key="translation_template")

    st.checkbox("Skip segmented", value=False, key="skip_segmented")
    st.button("Generate Flashcards", on_click=handle_csv_convert)

    if txt_file_path is not None:
        col1, col2 = st.columns([6, 2])
        with col1:
            st.success(f"Flashcards generated: {txt_file_path}")
        with col2:
            if is_local:
                st.button(
                    "Open file", 
                    key="open_flashcard_file",
                    use_container_width=True,
                    on_click=lambda: reveal_file_in_explorer(txt_file_path))
            else: 
                st.download_button(
                    "Download file",
                    get_txt_content(),
                    "flashcards.txt",
                    key="download_flashcard_file")

if txt_file_path is not None:
    txt_content = get_txt_content()

    st.write("#####")
    st.text_area("Generated Flashcards", txt_content, height=300)
    create_copy_button(st, "Copy to Clipboard", txt_content)