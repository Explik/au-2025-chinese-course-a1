import sys
import os
import csv

first_direction_template = "{text}\t{text} ({pinyin}) - {translation}\n"
second_direction_template = "{translation}\t{text} ({pinyin})\n"

one_way_template = first_direction_template
two_way_template = first_direction_template + second_direction_template

class CsvLine: 
    def __init__(self, text, pinyin, translation, is_sub_prase):
        self.text = text
        self.pinyin = pinyin
        self.translation = translation
        self.is_sub_prase = is_sub_prase

    def __str__(self):
        return f"Text: {self.text}, Pinyin: {self.pinyin}, Translation: {self.translation}, Sub Phrase Of: {self.sub_phrase_of}"

    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def from_csv_line(line):
        is_sub_prase = len(line[3]) > 0
        return CsvLine(line[0], line[1], line[2], is_sub_prase)
    
    @staticmethod
    def from_csv_file(file_path):
        with open(file_path, mode='r', newline='\n', encoding='utf-8-sig') as file:
            reader = csv.reader(file, delimiter=';')
            return [CsvLine.from_csv_line(line) for line in reader]

class FlashcardGenerator:
    SKIP_SEGMENTED = False
    TEMPLATE = "{text}\t{translation}\n"

    @staticmethod
    def generate_flashcard(csv_line):
        return FlashcardGenerator.TEMPLATE.format(
            text=csv_line.text, 
            pinyin=csv_line.pinyin, 
            translation=csv_line.translation)
    
    @staticmethod
    def generate_flashcards(csv_lines):
        filtered_lines = [line for line in csv_lines if not line.is_sub_prase] if FlashcardGenerator.SKIP_SEGMENTED else csv_lines
        return [FlashcardGenerator.generate_flashcard(line) for line in filtered_lines]

def deduplicate(csv_lines): 
    seen = set()
    deduplicated = []
    for line in csv_lines:
        if line.text not in seen:
            seen.add(line.text)
            deduplicated.append(line)
    return deduplicated

def process_file(csv_path):
    print("\nProcessing file: ", csv_path)

    lines = CsvLine.from_csv_file(csv_path)
    if not lines:
        print('No lines found in the CSV file')
        return
    
    filtered_lines = deduplicate(lines[1:])
    
    flashcards = FlashcardGenerator.generate_flashcards(filtered_lines)

    txt_path = csv_path.replace('.csv', '.txt')
    with open(txt_path, mode='w', newline='\n', encoding='utf-8') as txt_file:
            txt_file.writelines(flashcards)

    return txt_path

def main(path): 
    if os.path.isdir(path):
        csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not csv_files:
            print('No CSV files found in the directory')
            sys.exit(1)
        for csv_file in csv_files:
            process_file(os.path.join(path, csv_file))
    else:
        if not os.path.isfile(path):
            print('The provided path is not a valid file or directory')
            sys.exit(1)
        process_file(path)

if __name__ == "__main__":
    # Get csv/directory path from arguments 
    path = None 
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else: 
        print('Please provide a path to a CSV file')
        sys.exit(1)

    # Check for optional arguments
    if '--one-way' in sys.argv:
        print("Using one-way flashcard template")
        FlashcardGenerator.TEMPLATE = first_direction_template
    else: 
        print("Using two-way flashcard template")
        FlashcardGenerator.TEMPLATE = two_way_template

    if '--skip-segmented' in sys.argv:
        print("Skipping segmented phrases")
        FlashcardGenerator.SKIP_SEGMENTED = True
        
    main(path)