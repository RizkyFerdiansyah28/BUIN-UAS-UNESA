# buin/views.py

from django.shortcuts import render
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os
from django.conf import settings
import json

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
        df_genre = pd.read_csv(file_path).sort_values('release_year') #

        genres = df_genre['genre'].unique()
        
        charts_data = []

        for genre in genres:
            genre_data = df_genre[df_genre['genre'] == genre]
            if len(genre_data) < 2:
                continue

            X = genre_data[['release_year']]
            y = genre_data['count']

            # Data asli untuk scatter plot
            actual_data_points = [{'x': r, 'y': c} for r, c in zip(X['release_year'], y)]

            # Membuat model regresi
            model = LinearRegression()
            model.fit(X, y)

            # Membuat data untuk garis tren
            min_year, max_year = int(X['release_year'].min()), int(X['release_year'].max())
            future_year = max_year + 5
            
            x_trend = np.array([min_year, future_year]).reshape(-1, 1)
            y_trend = model.predict(x_trend)
            
            trend_line_points = [{'x': x_trend[0][0], 'y': y_trend[0]}, {'x': x_trend[1][0], 'y': y_trend[1]}]

            chart_data = {
                'title': f'Analisis Tren Genre: {genre}',
                'datasets': [
                    {
                        'label': 'Data Asli',
                        'data': actual_data_points,
                        'backgroundColor': 'rgba(54, 162, 235, 1)',
                        'type': 'scatter',
                    },
                    {
                        'label': 'Garis Tren',
                        'data': trend_line_points,
                        'borderColor': 'rgba(255, 99, 132, 1)',
                        'backgroundColor': 'rgba(255, 99, 132, 1)',
                        'type': 'line',
                        'fill': False,
                        'tension': 0.1
                    }
                ]
            }
            charts_data.append(chart_data)
        
        return render(request, 'buin/genre_prediction.html', {
            'charts_data_json': json.dumps(charts_data, cls=NumpyEncoder)
        })

    except FileNotFoundError:
        return render(request, 'buin/error.html', {'message': "File 'popular_genre_per_year.csv' not found."})

def actor_prediction(request):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'actor_trend_data.csv')
        df_actor = pd.read_csv(file_path).sort_values('release_year') #
        df_actor = df_actor[~df_actor['stars'].isin(['Stars:', 'Star:'])] #

        top_actors = df_actor.groupby('stars')['appearance_count'].sum().nlargest(5).index.tolist() #

        charts_data = []

        for actor in top_actors:
            actor_data = df_actor[df_actor['stars'] == actor]
            if len(actor_data) < 2:
                continue
            
            X = actor_data[['release_year']]
            y = actor_data['appearance_count']

            # Data asli untuk scatter plot
            actual_data_points = [{'x': r, 'y': c} for r, c in zip(X['release_year'], y)]

            # Membuat model regresi
            model = LinearRegression()
            model.fit(X, y)

            # Membuat data untuk garis tren
            min_year, max_year = int(X['release_year'].min()), int(X['release_year'].max())
            future_year = max_year + 5
            
            x_trend = np.array([min_year, future_year]).reshape(-1, 1)
            y_trend = model.predict(x_trend)
            
            trend_line_points = [{'x': x_trend[0][0], 'y': y_trend[0]}, {'x': x_trend[1][0], 'y': y_trend[1]}]

            chart_data = {
                'title': f'Analisis Tren Aktor: {actor}',
                'datasets': [
                    {
                        'label': 'Data Asli',
                        'data': actual_data_points,
                        'backgroundColor': 'rgba(54, 162, 235, 1)',
                        'type': 'scatter',
                    },
                    {
                        'label': 'Garis Tren',
                        'data': trend_line_points,
                        'borderColor': 'rgba(255, 99, 132, 1)',
                        'backgroundColor': 'rgba(255, 99, 132, 1)',
                        'type': 'line',
                        'fill': False,
                        'tension': 0.1
                    }
                ]
            }
            charts_data.append(chart_data)

        return render(request, 'buin/actor_prediction.html', {
            'charts_data_json': json.dumps(charts_data, cls=NumpyEncoder)
        })
        
    except FileNotFoundError:
        return render(request, 'buin/error.html', {'message': "File 'actor_trend_data.csv' not found."})

def top_movies(request):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'top_10_rated_movies.csv')
        df_top_movies = pd.read_csv(file_path) #

        df_top_movies = df_top_movies.sort_values('votes', ascending=False).drop_duplicates('title').head(10) #
        df_top_movies = df_top_movies.sort_values('rating', ascending=False) #
        
        movies_data = df_top_movies.to_dict('records')

        return render(request, 'buin/top_movies.html', {'movies': movies_data})
    except FileNotFoundError:
        return render(request, 'buin/error.html', {'message': "File 'top_10_rated_movies.csv' not found."})