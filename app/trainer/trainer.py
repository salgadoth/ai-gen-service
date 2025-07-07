from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset

def fine_tune_t5(model_name = "t5-small", output_dir="./app/trainer/t5-trained", epochs=3):
    try:
        print("Loading dataset...")
        dataset = load_dataset("jfleg")
        train_data = dataset['validation']
        val_data = dataset['test']

        print("Loading tokenizer and model...")
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

        def preprocess(batch):
            inputs = ["correct: " + s for s in batch['sentence']]
            targets = [cor[0] if isinstance(cor, list) and len(cor) > 0 else "" for cor in batch["corrections"]]
            model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
            labels = tokenizer(targets, max_length=255, truncation=True, padding="max_length")
            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        print("Tokenizing data...")
        train_dataset = train_data.map(preprocess, batched=True)
        val_dataset = val_data.map(preprocess, batched=True)

        print("Setting up training arguments...")
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            save_total_limit=2,
            load_best_model_at_end=True,
        )

        data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

        print("Starting training...")
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )

        trainer.train()
        print("Saving model...")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"Model and tokenizer saved to {output_dir}")
    except Exception as e:
        print(f"Error during training: {e}")

if __name__ == "__main__":
    fine_tune_t5()