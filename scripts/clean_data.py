import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from deep_translator import GoogleTranslator
from pathlib import Path
from random_username.generate import generate_username

class DataCleaner:
    def __init__(self, data: pd.DataFrame, state: str):
        self.data = data
        self.cleaned_data = None
        self.state = state
        self.username_map = {}

    def anonymize_usernames(self):
        """
        Anonymizes usernames by replacing them with random unique words, preferring fruits and objects.
        """
        unique_usernames = self.data['author_name'].unique()
        new_usernames = generate_username(len(unique_usernames))

        self.username_map = {original: new for original, new in zip(unique_usernames, new_usernames)}
        self.data['author_name'] = self.data['author_name'].map(self.username_map)

    def clean_data(self):
        """
        This method cleans the data by removing special characters, digits, and stopwords.
        """
        self.anonymize_usernames()

        # Add state column
        self.data['state'] = self.state

        # Remove special characters and digits
        # Clean 'body' column
        self.data['cleaned_body'] = self.data['body'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', str(x)))
        self.data['cleaned_body'] = self.data['cleaned_body'].apply(lambda x: re.sub(r'\d+', '', x))

        # Clean 'comment_body' column
        self.data['cleaned_comment_body'] = self.data['comment_body'].apply(
            lambda x: re.sub(r'[^a-zA-Z\s]', '', str(x)))
        self.data['cleaned_comment_body'] = self.data['cleaned_comment_body'].apply(lambda x: re.sub(r'\d+', '', x))

        # Remove stopwords in German
        nltk.download('stopwords')
        nltk.download('punkt')
        stop_words = set(stopwords.words('german'))
        self.data['cleaned_body'] = self.data['cleaned_body'].apply(
            lambda x: ' '.join([word for word in word_tokenize(x) if word.lower() not in stop_words]))

        self.data['cleaned_comment_body'] = self.data['cleaned_comment_body'].apply(
            lambda x: ' '.join([word for word in word_tokenize(x) if word.lower() not in stop_words]))

        # Translate the text to English
        self.data['cleaned_body'] = self.data['cleaned_body'].apply(
            lambda x: GoogleTranslator(source='auto', target='en').translate(x) if not x.isascii() else x)

        self.data['cleaned_comment_body'] = self.data['cleaned_comment_body'].apply(
            lambda x: GoogleTranslator(source='auto', target='en').translate(x) if not x.isascii() else x)
        self.cleaned_data = self.data

    def save_cleaned_data(self, file_path: str):
        """
        This method saves the cleaned data to a .csv file.
        """
        if self.cleaned_data is not None:
            file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            self.cleaned_data.to_csv(file_path, mode='a', header=not file_path.exists(), index=False)


if __name__ == "__main__":
    files_states = {
        "burgenland_politik_posts.csv": "Burgenland",
        "kaernten_politik_posts.csv": "Kaernten",
        "linz_politik_posts.csv": "Linz",
        "niederoesterreich_politik_posts.csv": "Niederoesterreich",
        "salzburg_politik_posts.csv": "Salzburg",
        "steiermark_politik_posts.csv": "Steiermark",
        "tirol_politik_posts.csv": "Tirol",
        "vorarlberg_politik_posts.csv": "Vorarlberg",
        "wien_politik_posts.csv": "Wien",
        "austria_politik_posts.csv": "Austria",
        "europe_politik_posts.csv": "Europe"
    }

    output_file = Path.cwd() / "subreddits_datafiles/processed_datafiles/cleaned_data1.csv"
    
    for file_name, state in files_states.items():
        dataset_path = Path.cwd() / 'subreddits_datafiles' / file_name
        if dataset_path.exists():
            print(f"Processing {file_name} for state {state}")
            data = pd.read_csv(dataset_path)
            cleaner = DataCleaner(data, state)
            cleaner.clean_data()
            cleaner.save_cleaned_data(output_file)
        else:
            print(f"File {file_name} does not exist at {dataset_path}")
