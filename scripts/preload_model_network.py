
from transformers import pipeline

# Preload the model
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
