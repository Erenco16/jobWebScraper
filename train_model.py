import json
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

MODEL_NAME = "distilbert-base-uncased"
DATA_PATH = "data/gradireland_jobs.json"
OUTPUT_DIR = "trained_model"

def load_data(path=DATA_PATH):
    """Load job description data from JSON file"""
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    descriptions = [item["description"] for item in raw_data]
    labels = [item["label"] for item in raw_data]
    return descriptions, labels

def prepare_datasets(texts, labels, test_size=0.2):
    """Split data into train and validation Hugging Face Datasets"""
    train_texts, val_texts, train_labels, val_labels = train_test_split(texts, labels, test_size=test_size)
    train_dataset = Dataset.from_dict({"text": train_texts, "label": train_labels})
    val_dataset = Dataset.from_dict({"text": val_texts, "label": val_labels})
    return train_dataset, val_dataset

def tokenize_dataset(train_dataset, val_dataset, tokenizer):
    """Tokenize datasets using provided tokenizer"""
    def tokenize(batch):
        return tokenizer(batch["text"], padding=True, truncation=True)
    train_dataset = train_dataset.map(tokenize, batched=True)
    val_dataset = val_dataset.map(tokenize, batched=True)
    return train_dataset, val_dataset

def build_model(model_name=MODEL_NAME):
    """Load pretrained transformer model for binary classification"""
    return AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

def train_model(model, train_dataset, val_dataset):
    """Train the model using Hugging Face Trainer API"""
    training_args = TrainingArguments(
        output_dir="./results",
        logging_dir="./logs",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )
    trainer.train()
    return trainer

def save_model(trainer, tokenizer, output_dir=OUTPUT_DIR):
    """Save the trained model and tokenizer"""
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)


def main():
    texts, labels = load_data()
    train_dataset, val_dataset = prepare_datasets(texts, labels)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_dataset, val_dataset = tokenize_dataset(train_dataset, val_dataset, tokenizer)
    model = build_model()
    trainer = train_model(model, train_dataset, val_dataset)
    save_model(trainer, tokenizer)


if __name__ == "__main__":
    main()