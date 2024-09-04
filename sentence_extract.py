import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

model_name = "google/gemma-2-9b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()

input_file = 'earthquake_extraction.jsonl'
output_file_jsonl = 'earthquake_fatalities_number_sentences.jsonl'

def extract_sentences_with_numbers_using_llm(body):
    prompt = f"Article: {body}\n\nPlease extract all sentences from this article that mention numbers, especially fatalities and injuries. Start every extracted sentence with a hyphen ('-'). If no sentence contains numbers, respond with 'no'."
    inputs = tokenizer(prompt, return_tensors="pt")
    
    
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
    return response_text  # Return the extracted sentences with numbers

with open(input_file, 'r') as infile, open(output_file_jsonl, 'w') as jsonl_file:
    lines = infile.readlines()

    for line in tqdm(lines, desc="Processing lines"):
        try:
            data = json.loads(line)
          
            url = data.get('url', 'No URL')
            title = data.get('title', '')
            body = data.get('body', '')

            number_sentences = extract_sentences_with_numbers_using_llm(body)

            # Write the result to the JSONL file
            output_data = {
                'url': url,
                'title': title,
                'number_sentences': number_sentences  # Save extracted number sentences
            }
            jsonl_file.write(json.dumps(output_data) + '\n')

        except Exception as e:
            # Skip to the next item if an exception occurs
            print(f"Skipping entry due to error: {e}")
            continue

print(f"Results saved to {output_file_jsonl}")
