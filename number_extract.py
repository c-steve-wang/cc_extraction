import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = "google/gemma-2-9b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
model.eval()

input_file = 'earthquake_extraction.jsonl'
output_file_jsonl = 'earthquake_fatalities_number_sentences.jsonl'

def extract_death_and_fatality_numbers(body, title):
    prompt = f"Here are the title {title} an article: {body}\n\nPlease identify the number of deaths and injuries mentioned in the title and the article , ensuring explicitly mentioned the year other than 2023 is excluded. If no deaths are mentioned, respond with 'None'."
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

with open(input_file, 'r') as infile, open(output_file_jsonl, 'w') as jsonl_file:
    lines = infile.readlines()

    for line in tqdm(lines, desc="Processing lines"):
        try:
            data = json.loads(line)
            url = data.get('url', 'No URL')
            title = data.get('title', '')
            body = data.get('body', '')

            resposne = extract_death_and_fatality_numbers(body, title)

            output_data = {
                'url': url,
                'title': title,
                'response': response
            }
            jsonl_file.write(json.dumps(output_data) + '\n')

        except Exception as e:
            continue

print(f"Results saved to {output_file_jsonl}")
