import json
import torch
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Extract sentences mentioning numbers from articles using an LLM")
    parser.add_argument('--model_name', type=str, default="google/gemma-2-9b-it", help="The name of the model to use")
    parser.add_argument('--input_file', type=str, default='earthquake_extraction.jsonl', help="Path to the input file in JSONL format")
    parser.add_argument('--output_file', type=str, default='earthquake_fatalities_number_sentences.jsonl', help="Path to the output JSONL file")
    return parser.parse_args()

def extract_sentences_with_numbers_using_llm(body, tokenizer, model, device):
    prompt = f"Article: {body}\n\nPlease extract all sentences from this article that mention numbers, especially fatalities and injuries. Start every extracted sentence with a hyphen ('-'). If no sentence contains numbers, respond with 'no'."
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_new_tokens=250,  
            num_return_sequences=1,
            do_sample=False
        )
    
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    if response_text.lower() == 'no':
        return ''
    return response_text  


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

                number_sentences = extract_sentences_with_numbers_using_llm(body, tokenizer, model, device)
                
                output_data = {
                    'url': url,
                    'title': title,
                    'number_sentences': number_sentences  
                }
                jsonl_file.write(json.dumps(output_data) + '\n')

            except Exception as e:
                print(f"Skipping entry due to error: {e}")
                continue

    print(f"Results saved to {args.output_file}")

if __name__ == "__main__":
    main()
