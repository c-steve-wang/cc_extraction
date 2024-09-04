# The primary objective is to evaluate whether changing the GPU and model size (>= 13B) affects performance.

```bash
python number_extract.py --model_name "google/gemma-2-27b-it" \
                         --output_file "output_number_27b.jsonl"
```

```bash
python sentence_extract.py --model_name "google/gemma-2-27b-it" \
                           --output_file "output_sentence_27b.jsonl"
```

