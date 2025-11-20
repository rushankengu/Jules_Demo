import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Path to the data file
DATA_PATH = r'C:\Users\risha\Documents\Project\Major Project\proj\MajorProject\proj\data_cleaned.csv'

def generate_models():
    print(f"Loading data from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print(f"Error: File not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Ensure 'soup' column exists
    if 'soup' not in df.columns:
        print("Error: 'soup' column missing in data.")
        return

    print("Generating Count Matrix...")
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(df['soup'].astype(str))

    print("Calculating Cosine Similarity...")
    # Note: This is memory intensive for large datasets
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    print("Saving pickle files...")
    with open('products_dict.pkl', 'wb') as f:
        pickle.dump(df.to_dict(), f)

    with open('similarity.pkl', 'wb') as f:
        pickle.dump(cosine_sim, f)
    
    print("Models generated successfully.")

if __name__ == '__main__':
    generate_models()
