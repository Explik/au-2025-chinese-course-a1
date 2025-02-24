import asyncio
from pypdf import PdfReader
import re
import pinyin
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import csv
import sys
import os

# Simple functions 
def extract_text_from_pdf(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    return ' '.join(page.extract_text() for page in pdf_reader.pages)

def filter_chinese_characters(text):
    chinese_signs = re.findall(r'[\u4e00-\u9fff]+', text)
    return ' '.join(chinese_signs)

def generate_pinyin(text):
    return pinyin.get(text, delimiter=' ')

def has_wiktionary_entry(chinese_phrase):
    url = f'https://en.wiktionary.org/wiki/{chinese_phrase}'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        chinese_section = soup.find('h2', id='Chinese')
        return chinese_section is not None
    else:
        return False
    
def extract_combinations(text):
    combinations = set()
    length = len(text)
    
    for i in range(length):
        for j in range(i + 1, length + 1):
            combinations.add(text[i:j])

    combinations.remove(text)
    
    sorted_combinations = sorted(combinations, key=lambda x: (len(x), text.index(x)))

    return list(sorted_combinations)

def extract_chinese_sub_phrases(chinese_phrase):
    potential_sub_phrases = extract_combinations(chinese_phrase)

    valid_sub_phrases = []
    for sub_phrase in potential_sub_phrases:
        if has_wiktionary_entry(sub_phrase):
            valid_sub_phrases.append(sub_phrase)

    return valid_sub_phrases

async def translateAsync(text, target_language):
    translator = Translator()
    translation = await translator.translate(text, dest=target_language)
    return translation.text

def write_csv_line(file, writer, elements):
    print('\t\t\t'.join(elements))
    writer.writerow(elements)
    file.flush()

class ChinesePhrase:
    CACHE = {}
    SUB_PHRASE_LIMIT = 6
    SKIP_SEGMENTATION = False
    SKIP_TRANSLATION = False
    
    def __init__(self, text, pinyin, translation=None, sub_phrases=None):
        self.text = text
        self.pinyin = pinyin
        self.translation = translation
        self.sub_phrases = sub_phrases or []

    def __str__(self):
        return f'{self.text} ({self.pinyin})'

    @staticmethod
    async def create_async(text):
        if text in ChinesePhrase.CACHE:
            return ChinesePhrase.CACHE[text]

        pinyin_text = generate_pinyin(text)
        translation = await translateAsync(text, 'da') if not ChinesePhrase.SKIP_TRANSLATION else ''
        
        instance =  ChinesePhrase(text, pinyin_text, translation)
        ChinesePhrase.CACHE[text] = instance
        return instance
    
    @staticmethod
    async def create_with_sub_phrases_async(phrase):
        if phrase in ChinesePhrase.CACHE:
            return ChinesePhrase.CACHE[phrase]

        if len(phrase) > ChinesePhrase.SUB_PHRASE_LIMIT: 
            return await ChinesePhrase.create_async(phrase)
        
        if ChinesePhrase.SKIP_SEGMENTATION:
            return await ChinesePhrase.create_async(phrase)

        instance = await ChinesePhrase.create_async(phrase)
        
        instance.sub_phrases = []
        for sub_phrase in extract_chinese_sub_phrases(phrase):
            sub_instance = await ChinesePhrase.create_async(sub_phrase)
            instance.sub_phrases.append(sub_instance)

        return instance

async def process_file_async(pdf_path, output_directory):
    print("\nProcessing file: ", pdf_path)
    pdf_file_name = os.path.basename(pdf_path)
    csv_file_name = pdf_file_name.replace('.pdf', '.csv')
    csv_file_path = os.path.join(output_directory, csv_file_name)

    pdf_text = extract_text_from_pdf(pdf_path)
    chinese_text = filter_chinese_characters(pdf_text)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(csv_file_path, mode='w', newline='\n', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        write_csv_line(file, writer, ['Text', 'Pinyin', 'Translation', 'Sub Phrase Of'])
                       
        for part in chinese_text.split():
            chinese_phrase = await ChinesePhrase.create_with_sub_phrases_async(part)
            write_csv_line(file, writer, [chinese_phrase.text, chinese_phrase.pinyin, chinese_phrase.translation, ''])
            
            for sub_phrase in chinese_phrase.sub_phrases:
                write_csv_line(file, writer, [sub_phrase.text, sub_phrase.pinyin, sub_phrase.translation, chinese_phrase.text])

    return csv_file_path

async def main_async(path, output_directory): 
    if os.path.isdir(path):
        pdf_files = [f for f in os.listdir(path) if f.endswith('.pdf')]
        if not pdf_files:
            print('No PDF files found in the directory')
            sys.exit(1)
        for pdf_file in pdf_files:
            await process_file_async(os.path.join(path, pdf_file), output_directory)
    else:
        if not os.path.isfile(path):
            print('The provided path is not a valid file or directory')
            sys.exit(1)
        await process_file_async(path, output_directory)

if __name__ == "__main__":
    # Get pdf/directory path from arguments 
    file_path = None 
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else: 
        print('Please provide a path to a PDF file')
        sys.exit(1)

    # Check for optional arguments
    output_directory = os.path.dirname(file_path)
    if '--output-directory' in sys.argv:
        output_index = sys.argv.index('--output-directory') + 1
        if output_index < len(sys.argv):
            output_directory = sys.argv[output_index]

            if "--" in output_directory:
                print('Please provide a valid output directory path')
                sys.exit(1)
        else:
            print('Please provide a valid output directory path')
            sys.exit(1)

    if '--skip-translation' in sys.argv or '--skip-all' in sys.argv:
        print("Skipping translation")
        ChinesePhrase.SKIP_TRANSLATION = True
        
    if '--skip-segmentation' in sys.argv or '--skip-all' in sys.argv:
        print("Skipping segmentation")
        ChinesePhrase.SKIP_SEGMENTATION = True
        
    asyncio.run(main_async(file_path, output_directory))
    