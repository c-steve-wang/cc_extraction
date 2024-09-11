import datetime
import requests
from urllib.parse import urljoin
import os
import gzip
import shutil
import argparse


# Base URL for the Common Crawl data
base_url = 'https://data.commoncrawl.org/'

# Function to parse date from filename
def parse_date_from_filename(filename):
    parts = filename.split('/')
    date_part = parts[-1].split('-')[2]
    date_str = date_part[:8]  # Get the date part from the timestamp
    return datetime.datetime.strptime(date_str, '%Y%m%d').date()

# Function to download a file
def download_file(url, target_folder, target_filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        target_path = os.path.join(target_folder, target_filename)
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Downloaded {target_filename} to {target_folder}')
        return target_path
    else:
        print(f'Failed to download {url}')
        return None

# Function to download and extract warc.paths.gz
def download_warc_paths(year, month, target_folder):
    warc_url = f'{base_url}crawl-data/CC-NEWS/{year}/{month:02}/warc.paths.gz'
    warc_gz_path = os.path.join(target_folder, 'warc.paths.gz')
    
    print(f'Starting download of {warc_url}...')
    gz_file = download_file(warc_url, target_folder, 'warc.paths.gz')
    
    if gz_file:
        extracted_file = os.path.join(target_folder, 'warc.paths')
        with gzip.open(gz_file, 'rb') as f_in:
            with open(extracted_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f'Extracted warc.paths.gz to {extracted_file}')
        return extracted_file
    return None

# Function to validate if the start and end dates are within the same month
def validate_dates(start_date, end_date):
    if start_date.year != end_date.year or start_date.month != end_date.month:
        raise ValueError("Start and end dates must be within the same month.")

# Function to check if the folder already exists
def check_folder_exists(folder_path):
    if os.path.exists(folder_path):
        raise FileExistsError(f"The folder '{folder_path}' already exists. Please provide a different folder name.")

# Function to remove temporary files
def remove_temp_files(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed temporary file: {file_path}")

# Main function to execute the logic
def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Download Common Crawl data based on date range.")
    parser.add_argument('--start_date', type=lambda d: datetime.datetime.strptime(d, '%Y/%m/%d').date(),
                        required=True, help="Start date in the format yyyy/mm/dd")
    parser.add_argument('--end_date', type=lambda d: datetime.datetime.strptime(d, '%Y/%m/%d').date(),
                        required=True, help="End date in the format yyyy/mm/dd")
    parser.add_argument('--save_folder', type=str, required=True, help="Folder where downloaded files will be stored")

    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    save_folder = args.save_folder

    # Validate that start and end dates are within the same month
    validate_dates(start_date, end_date)

    # Check if the folder already exists
    check_folder_exists(save_folder)

    # Create the save folder
    os.makedirs(save_folder)

    # Download and extract warc.paths.gz for the specified year and month
    year = start_date.year
    month = start_date.month

    warc_paths_file_path = download_warc_paths(year, month, save_folder)
    
    if warc_paths_file_path:
        # Read the warc.paths file and download files in the date range
        with open(warc_paths_file_path, 'r') as file:
            for line in file:
                filename = line.strip()
                file_date = parse_date_from_filename(filename)

                # Check if the file's date falls within the specified range
                if start_date <= file_date <= end_date:
                    # Directly use the full relative path from the warc.paths file
                    file_url = urljoin(base_url, filename)
                    target_filename = filename.split('/')[-1]  # Extract the filename from the path
                    print(f'Starting download of {file_url}...')
                    download_file(file_url, save_folder, target_filename)

        print('Download process completed.')

        # Remove the warc.paths and warc.paths.gz files after processing
        remove_temp_files(warc_paths_file_path, os.path.join(save_folder, 'warc.paths.gz'))
    else:
        print('Failed to download or extract warc.paths.gz')

if __name__ == '__main__':
    main()
