from flask import Flask, render_template, request, redirect
import pandas as pd
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)


# READ DATASET

df = pd.read_csv(
    "dataset/mymoviedb.csv",
    engine='python',
    on_bad_lines='skip'
)


# CLEAN DATA

df['Vote_Average'] = pd.to_numeric(
    df['Vote_Average'],
    errors='coerce'
)

df['Popularity'] = pd.to_numeric(
    df['Popularity'],
    errors='coerce'
)

df['Genre'] = df['Genre'].fillna('')

df['Title'] = df['Title'].fillna('')

df['Poster_Url'] = df['Poster_Url'].fillna('')


# CREATE DATABASE

conn = sqlite3.connect("netflix.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_name TEXT
)
""")

conn.commit()

conn.close()


# ML MODEL

tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix = tfidf.fit_transform(df['Genre'])


# RECOMMEND FUNCTION

def recommend_movies(movie_name):

    movie_name = movie_name.lower()

    matching_movies = df[
        df['Title'].str.lower().str.contains(
            movie_name,
            na=False
        )
    ]

    if matching_movies.empty:
        return ["Movie Not Found"]

    movie_index = matching_movies.index[0]

    similarity_scores = list(
        enumerate(
            cosine_similarity(
                tfidf_matrix[movie_index],
                tfidf_matrix
            )[0]
        )
    )

    sorted_movies = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommended_movies = []

    for movie in sorted_movies[1:6]:

        index = movie[0]

        title = df.iloc[index]['Title']

        genre = df.iloc[index]['Genre']

        rating = df.iloc[index]['Vote_Average']

        poster = df.iloc[index]['Poster_Url']

        recommended_movies.append({

            'title': title,
            'genre': genre,
            'rating': rating,
            'poster': poster

        })

    return recommended_movies


# HOME PAGE

@app.route('/', methods=['GET', 'POST'])
def home():

    total_records = len(df)

    average_rating = round(
        df['Vote_Average'].mean(),
        1
    )

    highest_popularity = round(
        df['Popularity'].max(),
        1
    )

    top_genre = df['Genre'].mode()[0]

    genre_counts = df['Genre'].value_counts().head(5)

    genres = genre_counts.index.tolist()

    counts = genre_counts.values.tolist()

    recommendations = []

    movie_name = ""

    # AUTOCOMPLETE MOVIES

    movie_titles = sorted(
        df['Title'].dropna().unique().tolist()
    )

    if request.method == 'POST':

        movie_name = request.form['movie_name']

        recommendations = recommend_movies(movie_name)

        if recommendations[0] != "Movie Not Found":

            conn = sqlite3.connect("netflix.db")

            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO search_history (movie_name) VALUES (?)",
                (movie_name,)
            )

            conn.commit()

            conn.close()

    conn = sqlite3.connect("netflix.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, movie_name
    FROM search_history
    ORDER BY id DESC
    LIMIT 5
    """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        total_records=total_records,
        average_rating=average_rating,
        highest_popularity=highest_popularity,
        top_genre=top_genre,
        genres=genres,
        counts=counts,
        recommendations=recommendations,
        movie_name=movie_name,
        history=history,
        movie_titles=movie_titles
    )


# CLICK HISTORY SEARCH

@app.route('/search/<movie_name>', methods=['GET'])
def search_movie(movie_name):

    recommendations = recommend_movies(movie_name)

    total_records = len(df)

    average_rating = round(
        df['Vote_Average'].mean(),
        1
    )

    highest_popularity = round(
        df['Popularity'].max(),
        1
    )

    top_genre = df['Genre'].mode()[0]

    genre_counts = df['Genre'].value_counts().head(5)

    genres = genre_counts.index.tolist()

    counts = genre_counts.values.tolist()

    movie_titles = sorted(
        df['Title'].dropna().unique().tolist()
    )

    conn = sqlite3.connect("netflix.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, movie_name
    FROM search_history
    ORDER BY id DESC
    LIMIT 5
    """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        total_records=total_records,
        average_rating=average_rating,
        highest_popularity=highest_popularity,
        top_genre=top_genre,
        genres=genres,
        counts=counts,
        recommendations=recommendations,
        movie_name=movie_name,
        history=history,
        movie_titles=movie_titles
    )


# DELETE HISTORY

@app.route('/delete/<int:id>')
def delete_history(id):

    conn = sqlite3.connect("netflix.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM search_history WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect('/')


# RUN APP

if __name__ == '__main__':
    app.run(debug=True)
