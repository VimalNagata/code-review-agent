# Downloading the StarCoder Model

This directory is where you should download the StarCoder model for code analysis and test generation.

## Option 1: Using Hugging Face CLI

1. Install the Hugging Face CLI:
```bash
pip install huggingface_hub
```

2. Log in to Hugging Face:
```bash
huggingface-cli login
```

3. Download the model to this directory:
```bash
huggingface-cli download bigcode/starcoder --local-dir ./
```

## Option 2: Using Python Script

Create a `download_model.py` file in this directory with the following content:

```python
from huggingface_hub import snapshot_download
import os

# Set the directory for downloading
os.makedirs("./model", exist_ok=True)

# Download the model
snapshot_download(
    repo_id="bigcode/starcoder",
    local_dir="./model",
    ignore_patterns=["*.bin", "*.h5"],  # Skip large files for initial download
)
```

Then run it:
```bash
python download_model.py
```

## Option 3: Manual Download

1. Visit the model page: https://huggingface.co/bigcode/starcoder
2. Download the required files (config.json, tokenizer files, model files)
3. Place them in this directory

## Notes

- The full model is large (~15GB). Consider using a smaller model like "bigcode/starcoder2-1b" if you have limited resources.
- You can also use "bigcode/starcoderbase" which is the base model without the tokenizer.
- For production use, consider using a quantized version of the model to reduce memory usage.

## Testing the Model

After downloading, you can test if the model loads properly with:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("./model")
model = AutoModelForCausalLM.from_pretrained("./model")

# Test with a simple prompt
prompt = "def fibonacci(n):"
inputs = tokenizer(prompt, return_tensors="pt")
output = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```