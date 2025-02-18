# Chinese Text Extraction from PDFs

## Setup 
1. Install required python packages by running the following command in your terminal: 
```bash 
pip install -r requirements.txt
```

2. Configure authentication for the Google Translate API by following the instructions in [the Google Cloud Translation API documentation](https://cloud.google.com/translate/docs/setup). Otherwise, add the ```--skip-translation``` flag to the command line arguments when running the script.

## Usage 
To extract Chinese text from a PDF, run the following command in your terminal: 
```bash
py extract-chinese-from-pdfs.py < path_to_pdf_or_directory >
```

Ex. 
```bash
py extract-chinese-from-pdfs.py ./slides/1-kinas-sprog.pdf```
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