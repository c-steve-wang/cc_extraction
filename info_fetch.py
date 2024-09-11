import json
import torch
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

# Define argparse to take command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Extract death and fatality numbers from articles")
    parser.add_argument('--model_name', type=str, default="google/gemma-2-9b-it", help="The name of the model to use")
    parser.add_argument('--input_file', type=str, required=True, help="Input file in JSONL format")
    parser.add_argument('--output_file', type=str, required=True, help="Output file in JSONL format")
    return parser.parse_args()

# Extract death and fatality numbers from body and title
def extract_death_and_fatality_numbers(body, title, tokenizer, model, device):
    # Constructing a prompt that specifies the desired output format
    prompt = (f"Title: {title}\nBody: {body}\n\n"
              "Analyze the text and list the numbers of deaths and injuries reported. "
              "Format your response as follows:\n"
              "deaths: <number of deaths>\n"
              "injuries: <number of injuries>\n"
              "Exclude any events not from the current year, except for 2023. "
              "If no deaths or injuries are mentioned, put '0' for numbers.")

    # Tokenizing the prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Generating the response from the model
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_new_tokens=50,
            num_return_sequences=1,
            do_sample=False
        )

    # Decoding the generated tokens to text
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    print(response_text)

    # Parsing the response based on predefined format
    death_count = "0"
    injury_count = "0"
    response_lines = response_text.lower().split('\n')
    for line in response_lines:
        if "deaths:" in line:
            death_count = line.split(':')[1].strip()
        if "injuries:" in line:
            injury_count = line.split(':')[1].strip()

    # Structured output
    structured_response = f"deaths: {death_count}\ninjuries: {injury_count}"
    
    return structured_response


# Main function
def main():
    args = parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForCausalLM.from_pretrained(args.model_name).to(device)
    model.eval()

    with open(args.input_file, 'r') as infile, open(args.output_file, 'w') as jsonl_file:
        lines = infile.readlines()

        for line in tqdm(lines, desc="Processing lines"):
            try:
                data = json.loads(line)
                url = data.get('url', 'No URL')
                title = data.get('title', '')
                body = data.get('body', '')

                response = extract_death_and_fatality_numbers(body, title, tokenizer, model, device)

                # Parse the response to extract death and injury counts
                deaths, injuries = (resp.split(": ")[1] for resp in response.split('\n'))
                
                output_data = {
                    'url': url,
                    'title': title,
                    'deaths': deaths,
                    'injuries': injuries
                }
                jsonl_file.write(json.dumps(output_data) + '\n')

            except Exception as e:
                print(f"Failed to process line due to {e}")
                continue

    print(f"Results saved to {args.output_file}")

if __name__ == "__main__":
    main()
