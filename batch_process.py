import os
import subprocess
import argparse
from tqdm import tqdm

# Define argparse to take command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Process all JSONL files in the input folder and save results with '_extracted' suffix.")
    parser.add_argument('--input_folder', type=str, required=True, help="Folder containing input files in JSONL format")
    parser.add_argument('--output_folder', type=str, required=True, help="Folder to save output files")
    return parser.parse_args()

# Function to process JSONL files
def process_jsonl_files(input_folder, output_folder):
    model_name = "google/gemma-2-9b-it"  # The model name remains unchanged
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all JSONL files in the input folder
    jsonl_files = [f for f in os.listdir(input_folder) if f.endswith(".jsonl")]

    # Iterate through all files in the input folder using tqdm for progress display
    for filename in tqdm(jsonl_files, desc="Processing files", unit="file"):
        input_file = os.path.join(input_folder, filename)
        
        # Generate the output filename with the "_extracted" suffix
        output_filename = filename.replace(".jsonl", "_extracted.jsonl")
        output_file = os.path.join(output_folder, output_filename)
        
        # Call the db_warc.py script with the necessary arguments using subprocess
        subprocess.run([
            'python', 'db_warc.py', 
            '--model_name', model_name, 
            '--input_file', input_file, 
            '--output_file', output_file
        ])
        print(f"Processed {input_file} -> {output_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Process the JSONL files in the input folder and save the results to the output folder
    process_jsonl_files(args.input_folder, args.output_folder)
