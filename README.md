# Pipeline

## 1. Download the related warc files

```bash
python download_warc.py --start_date yyyy/mm/dd --end_date yyyy/mm/dd --save_folder path_to_save_folder
```

## 2. Keyword mathcing and format converter

```bash
python sentence_extract.py --model_name "google/gemma-2-27b-it" \
                           --output_file "output_sentence_27b.jsonl"
```

## 3. Single file LLM data extraction


### Optional: Batch processing
