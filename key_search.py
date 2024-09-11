import os
import argparse
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from tqdm import tqdm
import json

DetectorFactory.seed = 0

# Define the keyword "earthquake" in 10 different languages
keyword_translations = {
    'en': 'earthquake',  # English
    'zh-Hans': '地震',  # Simplified Chinese
    'zh-Hant': '地震',  # Traditional Chinese
    'es': 'terremoto',  # Spanish
    'ar': 'زلزال',  # Arabic
    'hi': 'भूकंप',  # Hindi
    'bn': 'ভূমিকম্প',  # Bengali
    'fr': 'tremblement de terre',  # French
    'ru': 'землетрясение',  # Russian
    'pt': 'terremoto',  # Portuguese
    'de': 'Erdbeben',  # German
    'tr': 'deprem',  # Turkish
    'ja': '地震',  # Japanese
    'ko': '지진',  # Korean
    'vi': 'động đất',  # Vietnamese
    'ta': 'நிலநடுக்கம்',  # Tamil
    'it': 'terremoto',  # Italian
    'pl': 'trzęsienie ziemi',  # Polish
    'uk': 'землетрус',  # Ukrainian
    'ro': 'cutremur',  # Romanian
    'nl': 'aardbeving',  # Dutch
    'th': 'แผ่นดินไหว',  # Thai
    'el': 'σεισμός',  # Greek
    'ms': 'gempa bumi',  # Malay
    'he': 'רעידת אדמה',  # Hebrew
    'fa': 'زلزله',  # Persian
    'sv': 'jordbävning',  # Swedish
    'id': 'gempa',  # Indonesian
    'hu': 'földrengés',  # Hungarian
    'fi': 'maanjäristys',  # Finnish
    'sr': 'земљотрес',  # Serbian
    'cs': 'zemětřesení',  # Czech
}



def process_warc_file(warc_file_path, output_jsonl_path):
    """Process a single WARC file and extract data matching the earthquake keyword."""
    url_count = 0

    # Open the WARC file and the output JSONL file
    with open(warc_file_path, 'rb') as stream, open(output_jsonl_path, 'w') as jsonl_file:
        # Wrap the iterator with tqdm for progress tracking
        for record in tqdm(ArchiveIterator(stream), desc=f"Processing {os.path.basename(warc_file_path)}", unit="record"):
            if record.rec_type == 'response':  # Only process HTTP response records
                # Extract URL and payload
                url = record.rec_headers.get_header('WARC-Target-URI')
                payload = record.content_stream().read()

                # Prepare the output data dictionary
                data = {
                    'url': url,
                    'content_type': record.http_headers.get_header('Content-Type', ''),
                    'title': None,
                    'body': None,
                    'language': None
                }

                # Parse the HTML content (if applicable)
                if 'text/html' in data['content_type']:
                    soup = BeautifulSoup(payload, 'html.parser')
                    title = soup.title.string if soup.title else None
                    body = soup.get_text(separator="\n").strip()

                    # Detect language and filter by keyword and language
                    if title:
                        try:
                            language = detect(body)
                            if language in keyword_translations:
                                translated_keyword = keyword_translations[language]
                                if translated_keyword.lower() in title.lower():
                                    data['title'] = title
                                    data['body'] = body
                                    data['language'] = language

                                    # Write the data dictionary to the JSONL file
                                    jsonl_file.write(json.dumps(data) + '\n')
                                    url_count += 1  # Increment the URL counter
                        except Exception:
                            # Handle any language detection errors
                            continue

    return url_count


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process WARC files in a folder and extract earthquake-related data.")
    parser.add_argument('--input_folder', type=str, required=True, help="Path to the folder containing WARC files")

    args = parser.parse_args()
    input_folder = args.input_folder

    # Create the output folder by appending "_jsonl_format" to the input folder name
    output_folder = f"{input_folder}_jsonl_format"
    os.makedirs(output_folder, exist_ok=True)

    # Get a list of all .warc.gz files in the input folder
    warc_files = [f for f in os.listdir(input_folder) if f.endswith('.warc.gz')]

    total_urls = 0

    # Process each WARC file
    for warc_file in warc_files:
        warc_file_path = os.path.join(input_folder, warc_file)
        output_jsonl_path = os.path.join(output_folder, warc_file.replace('.warc.gz', '.jsonl'))

        print(f"Processing WARC file: {warc_file}")
        url_count = process_warc_file(warc_file_path, output_jsonl_path)
        total_urls += url_count
        print(f"Processed {warc_file}: Found {url_count} URLs")

    # Print the total number of URLs found
    print(f"Total number of URLs found across all WARC files: {total_urls}")


if __name__ == "__main__":
    main()
