from django.shortcuts import render
from django.db.models import Sum
from sklearn.linear_model import LinearRegression
import numpy as np
import json
from .models import FactMovie, DimGenre, DimActor

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def index(request):
    """View untuk halaman utama."""
    return render(request, 'buin/index.html')

def genre_prediction(request):
    """Menampilkan prediksi tren genre dari data di database."""
    genres = DimGenre.objects.all()
    charts_data = []

    for genre in genres:
        # Ambil data dari database: tahun rilis dan jumlah kemunculan genre
        # .distinct() memastikan kita mendapat satu entri per tahun untuk genre ini
        genre_data_points = FactMovie.objects.filter(genre=genre)\
                                             .values('time__release_year', 'genre_appearance_count')\
                                             .distinct()\
                                             .order_by('time__release_year')

        if len(genre_data_points) < 2:
            continue

        X = np.array([d['time__release_year'] for d in genre_data_points]).reshape(-1, 1)
        y = np.array([d['genre_appearance_count'] for d in genre_data_points])

        # Data asli untuk scatter plot
        actual_data_points = [{'x': r[0], 'y': c} for r, c in zip(X, y)]

        # Buat model regresi
        model = LinearRegression()
        model.fit(X, y)

        # Buat data untuk garis tren
        min_year, max_year = int(X.min()), int(X.max())
        future_year = max_year + 5
        x_trend = np.array([min_year, future_year]).reshape(-1, 1)
        y_trend = model.predict(x_trend)
        trend_line_points = [{'x': x_trend[0][0], 'y': y_trend[0]}, {'x': x_trend[1][0], 'y': y_trend[1]}]

        charts_data.append({
            'title': f'Analisis Tren Genre: {genre.genre_name}',
            'datasets': [
                {'label': 'Data Asli', 'data': actual_data_points, 'backgroundColor': 'rgba(54, 162, 235, 1)', 'type': 'scatter'},
                {'label': 'Garis Tren', 'data': trend_line_points, 'borderColor': 'rgba(255, 99, 132, 1)', 'backgroundColor': 'rgba(255, 99, 132, 1)', 'type': 'line', 'fill': False}
            ]
        })

    return render(request, 'buin/genre_prediction.html', {
        'charts_data_json': json.dumps(charts_data, cls=NumpyEncoder)
    })

def actor_prediction(request):
    """Menampilkan prediksi tren aktor dari data di database."""
    # Ambil 5 aktor teratas berdasarkan jumlah total kemunculan
    top_actors = DimActor.objects.annotate(
        total_appearances=Sum('factmovie__actor_appearance_count')
    ).order_by('-total_appearances')[:5]

    charts_data = []

    for actor in top_actors:
        # Ambil data dari database: tahun rilis dan jumlah penampilan aktor
        actor_data_points = FactMovie.objects.filter(actor=actor)\
                                             .values('time__release_year', 'actor_appearance_count')\
                                             .distinct()\
                                             .order_by('time__release_year')

        if len(actor_data_points) < 2:
            continue

        X = np.array([d['time__release_year'] for d in actor_data_points]).reshape(-1, 1)
        y = np.array([d['actor_appearance_count'] for d in actor_data_points])

        # Data asli untuk scatter plot
        actual_data_points = [{'x': r[0], 'y': c} for r, c in zip(X, y)]

        # Buat model regresi
        model = LinearRegression()
        model.fit(X, y)

        # Buat data untuk garis tren
        min_year, max_year = int(X.min()), int(X.max())
        future_year = max_year + 5
        x_trend = np.array([min_year, future_year]).reshape(-1, 1)
        y_trend = model.predict(x_trend)
        trend_line_points = [{'x': x_trend[0][0], 'y': y_trend[0]}, {'x': x_trend[1][0], 'y': y_trend[1]}]

        charts_data.append({
            'title': f'Analisis Tren Aktor: {actor.actor_name}',
            'datasets': [
                {'label': 'Data Asli', 'data': actual_data_points, 'backgroundColor': 'rgba(54, 162, 235, 1)', 'type': 'scatter'},
                {'label': 'Garis Tren', 'data': trend_line_points, 'borderColor': 'rgba(255, 99, 132, 1)', 'backgroundColor': 'rgba(255, 99, 132, 1)', 'type': 'line', 'fill': False}
            ]
        })

    return render(request, 'buin/actor_prediction.html', {
        'charts_data_json': json.dumps(charts_data, cls=NumpyEncoder)
    })

def top_movies(request):
    """Menampilkan 10 film dengan rating tertinggi dari database."""
    # Filter untuk hanya menampilkan data yang memiliki rating (bukan data tren)
    top_movies_data = FactMovie.objects.filter(rating__gt=0)\
                                   .select_related('genre', 'actor', 'time')\
                                   .order_by('-rating')[:10]
    
    movies_context = []
    for movie in top_movies_data:
        movies_context.append({
            'title': movie.title,
            'rating': movie.rating,
            'votes': movie.votes,
            # Cek jika data ada sebelum mengaksesnya untuk menghindari error
            'release_year': movie.time.release_year if movie.time else 'N/A',
            'genre': movie.genre.genre_name if movie.genre else 'N/A',
            'stars': movie.actor.actor_name if movie.actor else 'N/A',
        })

    return render(request, 'buin/top_movies.html', {'movies': movies_context})