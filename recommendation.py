import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Read Dataset
df = pd.read_csv(
    "dataset/mymoviedb.csv",
    engine='python',
    on_bad_lines='skip'
)

# Fill Missing Genres
df['Genre'] = df['Genre'].fillna('')
df['Title'] = df['Title'].fillna('')

# Convert Genre Text into Numbers
tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix = tfidf.fit_transform(df['Genre'])

# Calculate Similarity
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Recommendation Function
def recommend_movies(movie_name):

    movie_name = movie_name.lower()

    matching_movies = df[df['Title'].str.lower().str.contains(movie_name)]

    if matching_movies.empty:
        return ["Movie Not Found"]

    movie_index = matching_movies.index[0]

    similarity_scores = list(enumerate(cosine_sim[movie_index]))

    sorted_movies = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommended_movies = []

    for movie in sorted_movies[1:6]:
        index = movie[0]
        title = df.iloc[index]['Title']
        recommended_movies.append(title)

    return recommended_movies


# Test Recommendation
movie = input("Enter Movie Name: ")

recommendations = recommend_movies(movie)

print("\nRecommended Movies:\n")

for movie in recommendations:
    print(movie)