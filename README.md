# Pipeline

## 1. Download the related warc files

```bash
python download_warc.py --start_date yyyy/mm/dd --end_date yyyy/mm/dd --save_folder path_to_save_folder
```

## 2. Keyword mathcing and format converter

```bash
python sentence_extract.py --input_folder path_to_save_folder   # the save folder from download 
```

## 3. Single file LLM data extraction
```bash
python info_fetch.py  --model_name hf_model_name \     # default set is "google/gemma-2-9b-it"
                      --input_file path_to_input.jsonl \
                      --output_file path_to_output.jsonl
```

### Optional: Batch processing
