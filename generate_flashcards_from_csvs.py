import sys
import os
import csv

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

def process_file(csv_path, output_directory):
    print("\nProcessing file: ", csv_path)

    try: 
        lines = CsvLine.from_csv_file(csv_path)
    except Exception as e:
        raise Exception(f"An error occurred while reading the CSV file: {e}")
    
    if not lines:
        raise Exception('No lines found in the CSV file')
    
    filtered_lines = deduplicate(lines[1:])
    
    flashcards = FlashcardGenerator.generate_flashcards(filtered_lines)

    csv_file_name = os.path.basename(csv_path)
    txt_file_name = csv_file_name.replace('.csv', '.txt')
    txt_file_path = os.path.join(output_directory, txt_file_name)
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(txt_file_path, mode='w', newline='\n', encoding='utf-8') as txt_file:
            txt_file.writelines(flashcards)

    return txt_file_path

def main(path, output_directory): 
    if os.path.isdir(path):
        csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not csv_files:
            print('No CSV files found in the directory')
            sys.exit(1)
        for csv_file in csv_files:
            process_file(os.path.join(path, csv_file), output_directory)
    else:
        if not os.path.isfile(path):
            print('The provided path is not a valid file or directory')
            sys.exit(1)
        process_file(path, output_directory)

if __name__ == "__main__":
    # Get csv/directory path from arguments 
    file_path = None 
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else: 
        print('Please provide a path to a CSV file')
        sys.exit(1)

    # Check for optional arguments
    # --output-directory [path]
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

    # --format [format_string]
    if '--format' in sys.argv:
        format_index = sys.argv.index('--format') + 1
        if format_index < len(sys.argv):
            format_string = sys.argv[format_index]

            if "--" in format_string:
                print('Please provide a valid format string')
                sys.exit(1)
            
            if len(format_string) == 0:
                print("Please provide a valid format string")
                sys.exit(1)

            FlashcardGenerator.TEMPLATE = format_string.replace("\\n", "\n").replace("\\t", "\t") + "\n"
        else:
            print('Please provide a valid format string')
            sys.exit(1)
    else: 
        print("Using default format string")
        FlashcardGenerator.TEMPLATE = "{text}\t{translation}\n"
    
    # --skip-segmented
    if '--skip-segmented' in sys.argv:
        print("Skipping segmented phrases")
        FlashcardGenerator.SKIP_SEGMENTED = True
        
    main(file_path, output_directory)