import time  # Added for timestamp fallback
from typing import cast

import dateparser
from datasets import Dataset as HFDataset
from datasets import load_dataset
from liqfit.collators import NLICollator
from liqfit.losses import FocalLoss
from liqfit.modeling import LiqFitModel
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    pipeline,  # Use transformers pipeline as fallback
)

# Load dataset
dataset = load_dataset("diwank/hn-upvote-data")

# Use data from the last 24 months
parsed_date = dateparser.parse("24 months ago")
# Use ternary operator for cleaner code
twenty_four_months_ago = (
    time.time() - (2 * 365 * 24 * 60 * 60) if parsed_date is None else parsed_date.timestamp()
)
dataset = dataset.filter(lambda d: d["time"] > twenty_four_months_ago)

# Load the base model and tokenizer
model_name = "answerdotai/ModernBERT-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Set up focal loss
loss_function = FocalLoss()  # Remove multi_target parameter which isn't supported

# Create LiqFit model
model = LiqFitModel(base_model.config, base_model, loss_func=loss_function)

# Create data collator
data_collator = NLICollator(tokenizer, max_length=256, padding=True, truncation=True)

# Define training arguments
args = TrainingArguments(
    output_dir="./trained-model",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    num_train_epochs=5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=False,
    report_to="none",
    fp16=True,
)

# Create trainer
# Get dataset splits safely with type ignores
# Using # type: ignore to suppress the specific error about __getitem__ on IterableDataset
train_split = dataset["train"]  # type: ignore
test_split = dataset["test"]  # type: ignore

# Cast to appropriate type for the trainer
train_dataset = cast(HFDataset, train_split)
test_dataset = cast(HFDataset, test_split)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train the model
trainer.train()

# Save the model locally
model.save_pretrained("./trained-model")
tokenizer.save_pretrained("./trained-model")

# Create pipeline for inference example
classification_pipeline = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

# Push to hub
model.push_to_hub("diwank/hn-upvote-classifier")
tokenizer.push_to_hub("diwank/hn-upvote-classifier")

print("Model training complete and model pushed to hub.")
