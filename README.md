Here’s the updated `README.md` to reflect the current state of your project, including use of a **pre-trained HuggingFace model**, externalized training, and FastAPI inference:

---

# ✨ T5 Grammar Correction API

A FastAPI-based microservice for grammar correction using a pre-trained [T5](https://huggingface.co/deep-learning-analytics/GrammarCorrector) model from HuggingFace. Designed to integrate seamlessly with writing assistant workflows.

---

## 🚀 Features

* ✅ **Grammar Correction** using a T5 model fine-tuned on the C4 dataset.
* ⚡️ **Inference-Only** mode—no local training required.
* 🔌 **REST API** exposed via FastAPI (`/predict` endpoint).
* 🔄 Easily swappable with any HuggingFace grammar correction model.

---

## 🧱 Project Structure

```
t5-grammar/
├── app/
│   ├── main.py                # FastAPI app entrypoint
│   ├── models/
│   │   └── grammar_corrector.py  # HuggingFace T5 model integration
│   ├── routes/
│   │   └── predict.py         # Inference route handler
│   ├── schemas/
│   │   └── prompt.py          # Pydantic schema for request/response
│   └── utils/
│       └── __init__.py        # Optional utility functions
├── trainer/                   # Optional: Fine-tuning module
│   └── trainer.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd t5-grammar
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI app

```bash
uvicorn app.main:app --reload
```

---

## 📡 API Usage

### `POST /predict`

Use this endpoint to submit a text string for grammar correction.

#### Request Body

```json
{
  "text": "your sentence with grammar mistake"
}
```

#### Response

```json
{
  "corrected": "your corrected sentence"
}
```

---

## 🧠 Model Details

* **Model**: [`deep-learning-analytics/GrammarCorrector`](https://huggingface.co/deep-learning-analytics/GrammarCorrector)
* **Architecture**: T5-base (pre-trained and fine-tuned)
* **Training Dataset**: [C4 200M](https://huggingface.co/datasets/c4)
* You may swap this out with any other HuggingFace grammar model in `grammar_corrector.py`.

---

## 🛠 Optional: Custom Training

If you'd like to train your own model using datasets like [JFLEG](https://huggingface.co/datasets/jhu-clsp/jfleg):

```bash
python trainer/trainer.py
```

The model will be saved to `trainer/t5-trained/`.

---

## 📝 Notes

* No GPU required for inference, but recommended for fine-tuning.
* Browser-based apps can offload grammar correction to this service via a simple POST request.

---

## 📄 License

MIT License