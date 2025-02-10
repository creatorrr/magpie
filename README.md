magpie
======

A simple model to predict what stories I'd like on HN so I don't doomscroll it.

Code is experimental but I believe anyone can run it easily.

```
poetry install
poetry shell

python -m magpie.prepare_dataset
python -m magpie.train
```

To convert to ONNX:
`optimum-cli export onnx --model diwank/hn-upvote-classifier --task feature-extraction --optimize O4 --device cuda --trust-remote-code hn-upvote-classifier-onnx`
