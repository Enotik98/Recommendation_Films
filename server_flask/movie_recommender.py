import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_recommenders as tfrs

# Завантаження даних з CSV.
data_url = "https://storage.googleapis.com/kagglesdsdata/datasets/2268437/3806003/IMDb_Data_final.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20230521%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20230521T104023Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=1cc3cc45f0e56956e069fe2180f113c9aeb6cd13569a01f2957d797c1a0e924da34a9d845b61040382a5d257a212d0814643535cfe23a593a85b8d972a45a81b77b29e4ce707e6895c58c8ad70bb37b6c8ec1ca29082d24e66a42bb8784a9dfc8207bb7282570d279ce518b2b4e109740237b003a73fbb9986af67f479a6f064549f34932d1916a2d9495733c839853dc231a6741f4717680604e93eadc208b9a022a2d69020c86b8c34aeca5fc1ff1643d1b969fe72e17c2de4ab606de695a2a8594e0624f7fee46ebd66638650fc90369c5a69bd674130fc751f7a6488f6b5299aabf6cf36061895e240a1c84a56b9620eb75f3dfa5a3daf9f426c023e1a84"
df = pd.read_csv(data_url)

# Попередня обробка даних.
df = df[["Title", "Director", "Stars", "IMDb-Rating", "Category", "Duration", "Censor-board-rating", "ReleaseYear"]]
df = df.dropna()  # Видалення рядків з відсутніми значеннями

# Конвертація даних в набори даних TensorFlow.
movies = tf.data.Dataset.from_tensor_slices(df["Title"])
ratings = tf.data.Dataset.from_tensor_slices({
    "movie_title": df["Title"],
    "user_id": df["Director"],  
    "release_year": df["ReleaseYear"]
})

# Визначення словників та моделей.
user_ids_vocabulary = tf.keras.layers.experimental.preprocessing.StringLookup()
user_ids_vocabulary.adapt(ratings.map(lambda x: x["user_id"]))

movie_titles_vocabulary = tf.keras.layers.experimental.preprocessing.StringLookup()
movie_titles_vocabulary.adapt(movies)

user_model = tf.keras.Sequential([
    user_ids_vocabulary,
    tf.keras.layers.Embedding(user_ids_vocabulary.vocab_size(), 64)
])

movie_model = tf.keras.Sequential([
    movie_titles_vocabulary,
    tf.keras.layers.Embedding(movie_titles_vocabulary.vocab_size(), 64)
])

class MovieRecommendationModel(tfrs.models.Model):
    def __init__(self, user_model, movie_model, movies_list):
        super().__init__()
        self.user_model = user_model
        self.movie_model = movie_model
        self.task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(movies.batch(128).map(movie_model)))
        self.movies_list = movies_list
        self.movie_titles_vocabulary = tf.keras.layers.experimental.preprocessing.StringLookup()
        self.movie_titles_vocabulary.adapt(movies_list)

    def compute_loss(self, features, training=False):
        user_embeddings = self.user_model(features["user_id"])
        positive_movie_embeddings = self.movie_model(features["movie_title"])
        return self.task(user_embeddings, positive_movie_embeddings)

    def get_recommendations(self, user_movies, genre=None, high_rating=False, num_recommendations=100):
        movies_list = self.movies_list

        if genre:
            genre_movies = []
            for g in genre.split(","):
                df_genre = df[df['Category'].str.contains(g)]
                genre_movies.extend(df_genre["Title"].tolist())
            movies_list = [movie for movie in movies_list if movie in genre_movies]

        if high_rating:
            high_rating_movies = df[df['IMDb-Rating'] >= 7.0]["Title"].tolist()
            movies_list = [movie for movie in movies_list if movie in high_rating_movies]

        user_movie_titles = tf.constant(user_movies)
        user_movie_ids = self.movie_titles_vocabulary(user_movie_titles)
        user_movie_ids = tf.strings.as_string(user_movie_ids)
        user_movie_embeddings = self.movie_model(user_movie_ids)
        movie_embeddings = self.movie_model.layers[-1].weights[0]
        scores = tf.matmul(user_movie_embeddings, tf.transpose(movie_embeddings))
        top_n_scores, top_n_idx = tf.math.top_k(scores, k=num_recommendations)
        recommended_movie_idxs = tf.reshape(top_n_idx, [-1])
        recommended_movie_scores = tf.reshape(top_n_scores, [-1])

        recommended_movie_idxs = recommended_movie_idxs.numpy()
        valid_indices = recommended_movie_idxs < len(movies_list)
        recommended_movie_idxs = recommended_movie_idxs[valid_indices]
        recommended_movie_scores = recommended_movie_scores[valid_indices]
        recommended_movie_idxs = np.unique(recommended_movie_idxs)

        recommended_movie_titles = [movies_list[i] for i in recommended_movie_idxs]

        return recommended_movie_titles, recommended_movie_scores

# Створення моделі пошуку.
model = MovieRecommendationModel(user_model, movie_model, df["Title"].tolist())  # Замінено `movies` на `df["Title"].tolist()`
model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

# Навчання моделі.
model.fit(ratings.batch(4096), epochs=3)

# Використання простого пошуку для підготовки пошуку з використанням навчених репрезентацій.
index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
index.index_from_dataset(movies.batch(100).map(lambda title: (title, model.movie_model(title))))
