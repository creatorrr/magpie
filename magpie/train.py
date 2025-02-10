from datasets import load_dataset
import dateparser
from setfit import SetFitModel, Trainer, TrainingArguments

model_name = "lightonai/modernbert-embed-large"
model = SetFitModel.from_pretrained(model_name, trust_remote_code=True)

dataset = load_dataset("diwank/hn-upvote-data")
dataset = dataset.filter(lambda d: d["time"] > dateparser.parse("3 years ago").timestamp())

args = TrainingArguments(
    sampling_strategy="oversampling",
    use_amp=True,
    batch_size=(256, 16),
    body_learning_rate=(4e-5, 2e-5),
    head_learning_rate=1e-2,
    warmup_proportion=0.05,
    l2_weight=0.2,
    evaluation_strategy="steps",
    eval_steps=2000,
    save_steps=2000,
    save_total_limit=2,
    end_to_end=True,
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    args=args,
)

setattr(trainer.args, "eval_strategy", trainer.args.evaluation_strategy)

trainer.train()
model.save_pretrained("./trained-model")
model.push_to_hub("diwank/hn-upvote-classifier")
