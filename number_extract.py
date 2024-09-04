import json
import torch
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Extract death and fatality numbers from articles")
    parser.add_argument('--model_name', type=str, default="google/gemma-2-9b-it", help="The name of the model to use")
    parser.add_argument('--input_file', type=str, default='earthquake_extraction.jsonl', help="Input file in JSONL format")
    parser.add_argument('--output_file', type=str, default='earthquake_fatalities_number_sentences.jsonl', help="Output file in JSONL format")
    return parser.parse_args()

def extract_death_and_fatality_numbers(body, title, tokenizer, model, device):
    prompt = f"Here are the title {title} an article: {body}\n\nPlease identify the number of deaths and injuries mentioned in the title and the article, ensuring explicitly mentioned the year other than 2023 is excluded. If no deaths are mentioned, respond with 'None'."
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_new_tokens=250,  
            num_return_sequences=1,
            do_sample=False
        )
    
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    if response_text.lower() == 'none':
        return ''
    return response_text

# Main function
def main():
    args = parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load the model and tokenizer using the provided model name
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForCausalLM.from_pretrained(args.model_name).to(device)
    model.eval()

    # Open input and output files
    with open(args.input_file, 'r') as infile, open(args.output_file, 'w') as jsonl_file:
        lines = infile.readlines()

        # Process each line in the input file
        for line in tqdm(lines, desc="Processing lines"):
            try:
                data = json.loads(line)
                url = data.get('url', 'No URL')
                title = data.get('title', '')
                body = data.get('body', '')

                # Extract response
                response = extract_death_and_fatality_numbers(body, title, tokenizer, model, device)

                # Prepare the output
                output_data = {
                    'url': url,
                    'title': title,
                    'response': response
                }
                jsonl_file.write(json.dumps(output_data) + '\n')

            except Exception as e:
                continue

    print(f"Results saved to {args.output_file}")

if __name__ == "__main__":
    main()
