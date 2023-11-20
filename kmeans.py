# -*- coding: utf-8 -*-
import PyPDF2
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
import pandas as pd

# Download NLTK stopwords
nltk.download('stopwords')
stop_words_set = stopwords.words('english')  # Note the change here

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() if page.extract_text() else ""
        return text

def extract_questions(text):
    # Define a regular expression pattern for SAT questions
    # Assumption: Each question starts with a number followed by a newline,
    # and ends just before the next problem number.
    question_pattern = re.compile(r'\n(\d+)\s+(.*?)(?=\n\d+\s|\Z)', re.DOTALL)

    # Find all matches of the pattern in the text
    matches = question_pattern.findall(text)

    # Return only the question text from each match
    return [match[1].strip() for match in matches]

def vectorize_questions(questions):
    vectorizer = TfidfVectorizer(stop_words=stop_words_set)
    X = vectorizer.fit_transform(questions)
    return X

def cluster_questions(X, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(X)
    return kmeans.labels_

# Main execution logic
if __name__ == "__main__":
    pdf_path = '/content/testsat.pdf'  # Replace with your PDF file path
    num_clusters = 5  # Adjust based on your needs

    # Extract text from PDF
    full_text = extract_text_from_pdf(pdf_path)
    # Extract individual questions from the text
    questions = extract_questions(full_text)

    # Check if we have extracted any questions
    if not questions:
        raise ValueError("No questions were extracted from the text. Please check the regex pattern and the PDF content.")

    # Vectorize the questions
    X = vectorize_questions(questions)

    # Cluster the questions
    cluster_labels = cluster_questions(X, num_clusters)

    # Create a DataFrame to view questions and their assigned clusters
    questions_df = pd.DataFrame({'Question': questions, 'Cluster': cluster_labels})
    print(questions_df)

    # Optionally, save the DataFrame to a CSV file for further analysis
    questions_df.to_csv('sat_questions_clusters.csv', index=False)
