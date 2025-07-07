# T5 Grammar Correction API

A FastAPI-based web service for grammar correction using a fine-tuned [T5-small](https://huggingface.co/t5-small) model on the [JFLEG](https://huggingface.co/datasets/jfleg) dataset.

## Features

- **Grammar Correction**: Accepts user text and returns a grammatically corrected version.
- **Fine-tuning**: Automatically fine-tunes T5-small on JFLEG if no trained model is found.
- **REST API**: Simple `/inference` endpoint for integration.

## Project Structure

```
app/
├── main.py                # FastAPI app entrypoint
├── models/
│   └── t5_model.py        # T5 model loading and inference
├── routes/
│   └── inference.py       # Inference API route
├── schemas/
│   └── prompt.py          # Pydantic schema for user input
├── trainer/
│   └── trainer.py         # Fine-tuning script
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd t5-grammar
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API**
   ```bash
   python app/main.py
   ```
   - If no fine-tuned model is found in `app/trainer/t5-trained/`, training will start automatically in the background.

## API Usage

### Endpoint

`POST /inference`

#### Request Body

```json
{
  "text": "your sentence with grammar mistake"
}
```

#### Response

```json
{
  "grammar_errors": "your corrected sentence"
}
```

## Training

- The trainer uses the JFLEG dataset and fine-tunes T5-small.
- Training is triggered automatically if no model is found, or you can run it manually:
  ```bash
  python app/trainer/trainer.py
  ```

## Notes

- For best performance, use a machine with a CUDA-enabled GPU. On Mac/CPU, training will be slower.
- The trained model and tokenizer are saved in `app/trainer/t5-trained/` (ignored by git).

## License

MIT