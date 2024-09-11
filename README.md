# Pipeline

## 1. Download the related warc files

```bash
python number_extract.py --model_name "google/gemma-2-27b-it" \
                         --output_file "output_number_27b.jsonl"
```

## 2. Keyword mathcing and format converter

```bash
python sentence_extract.py --model_name "google/gemma-2-27b-it" \
                           --output_file "output_sentence_27b.jsonl"
```

## 3. Single file LLM data extraction


### 3.1. Batch processing
