# Chinese-Danish flashcards generator from PDFs 
Simplify learning by extracting flashcards from your Chinese course slides (PDF-format-only).

The flashcards are generated in 3-steps: 
1. Extract chinese phrases from PDFs
    A. Extracts Chinese text from PDFs
    B. Expand on the Chinese text by segmenting it into meaningful subphrases (Optional). Meaningfulness is determined by the existence of a corrosponding english Wiktionary page.
    C. Generate pin yin for each phrase
    D. Generate Danish translations for each phrase (Optional)
    E. Output the extracted phrases to a CSV file
2. Generate flashcards from extracted phrases
    A. Generate flashcards for each phrase
    B. Output the flashcards to a TXT file
3. Import the flashcards to your favorite flashcard webpage (e.g. Quizlet)
    A. Create new flashcard set
    B. Import the flashcards from the TXT file

## Setup 
1. Install required python packages by running the following command in your terminal: 
```bash 
pip install -r requirements.txt
```

2. Configure authentication for the Google Translate API by following the instructions in [the Google Cloud Translation API documentation](https://cloud.google.com/translate/docs/setup). Otherwise, add the ```--skip-translation``` flag to the command line arguments when running the script.

## Usage (GUI)
To use the generator through a user interface, run the following command in your terminal: 
```bash
streamlit run generator_ui.py
``` 

If you want to debug the UI, you can run the script debug_generator_ui.py instead.


## Usage (CLI)
To extract Chinese text from a PDF, run the following command in your terminal: 
```bash
py extract-chinese-from-pdfs.py < path_to_pdf_or_directory >
```

Ex. 
```bash
py extract-chinese-from-pdfs.py ./slides/example.pdf --skip-all
```

Flags: 
- ```--skip-translation```: Skip translation of extracted Chinese text to Danish.
- ```--skip-segmentation```: Skip extraction of (sub)phrases from the Chinese text.
- ```--skip-all```: Skip both translation and segmentation of the extracted Chinese text.

To generate flashcards from (generated) CSVs, run the following command in your terminal: 
```bash
py generate-flashcards-from-csvs.py < path_to_csv_or_directory >
```

Flags: 
- ```--one-way```: Generate one-way flashcards (i.e. only from Chinese to Danish). Default is two-way flashcards (i.e. from Chinese to Danish and vice versa).
- ```--skip-segmented```: Skip all (sub)phrase flashcards. Default is to generate flashcards for all.