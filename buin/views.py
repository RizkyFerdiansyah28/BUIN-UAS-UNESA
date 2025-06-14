# buin/views.py

from django.shortcuts import render
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os
from django.conf import settings
import json

# LANGKAH 1: TAMBAHKAN CLASS PENERJEMAH INI
class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def get_random_color(alpha=1.0):
    """Helper function to generate random RGBA colors for charts."""
    return f"rgba({np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {alpha})"

def index(request):
    """View untuk halaman utama."""
    return render(request, 'buin/index.html')

def genre_prediction(request):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'popular_genre_per_year.csv')
        df_genre = pd.read_csv(file_path).sort_values('release_year')

        genres = df_genre['genre'].unique()
        
        all_years = sorted(list(df_genre['release_year'].unique()))
        future_years_list = list(range(all_years[-1] + 1, all_years[-1] + 6))
        chart_labels = all_years + future_years_list

        datasets = []

        for genre in genres:
            genre_data = df_genre[df_genre['genre'] == genre]
            if len(genre_data) < 2:
                continue

            actual_data_map = dict(zip(genre_data['release_year'], genre_data['count']))
            actual_counts = [actual_data_map.get(year) for year in all_years]

            model = LinearRegression()
            X = genre_data[['release_year']]
            y = genre_data['count']
            model.fit(X, y)

            last_actual_year = max(genre_data['release_year'])
            prediction_model_years = np.array([last_actual_year] + future_years_list).reshape(-1, 1)
            prediction_line_data = model.predict(prediction_model_years)

            actual_chart_data = actual_counts + [None] * len(future_years_list)
            prediction_chart_data = [None] * (len(all_years) - 1) + prediction_line_data.tolist()

            color = get_random_color(0.8)
            
            datasets.append({
                'label': f'{genre} (Actual)',
                'data': actual_chart_data,
                'borderColor': color,
                'backgroundColor': color,
                'fill': False,
            })
            datasets.append({
                'label': f'{genre} (Predicted)',
                'data': prediction_chart_data,
                'borderColor': color,
                'backgroundColor': color,
                'borderDash': [5, 5],
                'fill': False,
            })

        chart_data = {'labels': chart_labels, 'datasets': datasets}
        # LANGKAH 2: GUNAKAN PENERJEMAH DI FUNGSI INI
        return render(request, 'buin/genre_prediction.html', {'chart_data': json.dumps(chart_data, cls=NumpyEncoder)})

    except FileNotFoundError:
        return render(request, 'buin/error.html', {'message': "File 'popular_genre_per_year.csv' not found."})

def actor_prediction(request):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'actor_trend_data.csv')
        df_actor = pd.read_csv(file_path).sort_values('release_year')
        df_actor = df_actor[~df_actor['stars'].isin(['Stars:', 'Star:'])]

        top_actors = df_actor.groupby('stars')['appearance_count'].sum().nlargest(5).index.tolist()

        all_years = sorted(list(df_actor['release_year'].unique()))
        future_years_list = list(range(all_years[-1] + 1, all_years[-1] + 6))
        chart_labels = all_years + future_years_list

        datasets = []

        for actor in top_actors:
            actor_data = df_actor[df_actor['stars'] == actor]
            if len(actor_data) < 2:
                continue
            
            actual_data_map = dict(zip(actor_data['release_year'], actor_data['appearance_count']))
            actual_counts = [actual_data_map.get(year) for year in all_years]
            
            model = LinearRegression()
            X = actor_data[['release_year']]
            y = actor_data['appearance_count']
            model.fit(X, y)

            last_actual_year = max(actor_data['release_year'])
            prediction_model_years = np.array([last_actual_year] + future_years_list).reshape(-1, 1)
            prediction_line_data = model.predict(prediction_model_years)

            actual_chart_data = actual_counts + [None] * len(future_years_list)
            prediction_chart_data = [None] * (len(all_years) - 1) + prediction_line_data.tolist()

            color = get_random_color(0.8)

            datasets.append({'label': f'{actor} (Actual)', 'data': actual_chart_data, 'borderColor': color, 'backgroundColor': color, 'fill': False})
            datasets.append({'label': f'{actor} (Predicted)', 'data': prediction_chart_data, 'borderColor': color, 'backgroundColor': color, 'borderDash': [5, 5], 'fill': False})

        chart_data = {'labels': chart_labels, 'datasets': datasets}
        # LANGKAH 2 (lagi): GUNAKAN PENERJEMAH DI FUNGSI INI JUGA
        return render(request, 'buin/actor_prediction.html', {'chart_data': json.dumps(chart_data, cls=NumpyEncoder)})
        
    except FileNotFoundError:
        return render(request, 'buin/error.html', {'message': "File 'actor_trend_data.csv' not found."})

# Di dalam file buin/views.py

# ... (fungsi-fungsi lain seperti index, genre_prediction, dll. biarkan apa adanya)

def top_movies(request):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'top_10_rated_movies.csv')
        df_top_movies = pd.read_csv(file_path)

        df_top_movies = df_top_movies.sort_values('votes', ascending=False).drop_duplicates('title').head(10)
        df_top_movies = df_top_movies.sort_values('rating', ascending=False)
        
        labels = df_top_movies['title'].tolist()
        ratings = df_top_movies['rating'].tolist()
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Rating (out of 10)',
                'data': ratings,
                'backgroundColor': [get_random_color(0.7) for _ in range(len(labels))],
                'borderWidth': 1
            }]
        }
        
        movies_data = df_top_movies.to_dict('records')

        # PERBAIKAN: Gunakan NumpyEncoder di sini juga untuk konsistensi
        return render(request, 'buin/top_movies.html', {
            'chart_data': json.dumps(chart_data, cls=NumpyEncoder),
            'movies': movies_data
        })
    except FileNotFoundError:
        return render(request, 'buin/error.html', {'message': "File 'top_10_rated_movies.csv' not found."})