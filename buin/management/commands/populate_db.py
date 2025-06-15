import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from buin.models import DimActor, DimGenre, DimTime, FactMovie
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates the database from CSV files.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population process...'))

        # Path ke file-file CSV
        path_actor_trend = os.path.join(settings.BASE_DIR, 'actor_trend_data.csv')
        path_genre_trend = os.path.join(settings.BASE_DIR, 'popular_genre_per_year.csv')
        path_top_movies = os.path.join(settings.BASE_DIR, 'top_10_rated_movies.csv')

        with transaction.atomic():
            # Hapus data lama untuk memulai dari awal
            self.stdout.write('Deleting old data...')
            FactMovie.objects.all().delete()
            DimActor.objects.all().delete()
            DimGenre.objects.all().delete()
            DimTime.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Old data deleted.'))

            # --- 1. Isi data dari actor_trend_data.csv ---
            self.stdout.write('Populating from actor_trend_data.csv...')
            df_actor_trend = pd.read_csv(path_actor_trend)
            for _, row in df_actor_trend.iterrows():
                try:
                    actor_name = str(row['stars']).strip()
                    # Lewati baris yang tidak valid seperti 'Stars:' atau 'Star:'
                    if not actor_name or pd.isna(actor_name) or "Stars:" in actor_name or "Star:" in actor_name:
                        continue
                    
                    actor_obj, _ = DimActor.objects.get_or_create(actor_name=actor_name)
                    time_obj, _ = DimTime.objects.get_or_create(release_year=int(row['release_year']))
                    
                    # Buat entri fakta khusus untuk data tren aktor
                    FactMovie.objects.create(
                        actor=actor_obj,
                        time=time_obj,
                        actor_appearance_count=int(row['appearance_count']),
                        title=f"Actor Trend: {actor_name} ({row['release_year']})", # Judul placeholder
                    )
                except (ValueError, TypeError):
                    continue # Lewati baris jika ada data yang salah format

            # --- 2. Isi data dari popular_genre_per_year.csv ---
            self.stdout.write('Populating from popular_genre_per_year.csv...')
            df_genre_trend = pd.read_csv(path_genre_trend)
            for _, row in df_genre_trend.iterrows():
                try:
                    genre_name = str(row['genre']).strip()
                    if not genre_name or pd.isna(genre_name):
                        continue

                    genre_obj, _ = DimGenre.objects.get_or_create(genre_name=genre_name)
                    time_obj, _ = DimTime.objects.get_or_create(release_year=int(row['release_year']))
                    
                    # Buat entri fakta khusus untuk data tren genre
                    FactMovie.objects.create(
                        genre=genre_obj,
                        time=time_obj,
                        genre_appearance_count=int(row['count']),
                        title=f"Genre Trend: {genre_name} ({row['release_year']})", # Judul placeholder
                    )
                except (ValueError, TypeError):
                    continue

            # --- 3. Isi data dari top_10_rated_movies.csv ---
            self.stdout.write('Populating from top_10_rated_movies.csv...')
            df_top_movies = pd.read_csv(path_top_movies)
            for _, row in df_top_movies.iterrows():
                try:
                    # File ini tidak memiliki info tahun, genre, atau aktor.
                    # Kita hanya akan menyimpan data yang ada.
                    FactMovie.objects.create(
                        title=str(row['title']).strip(),
                        rating=float(row['rating']),
                        votes=int(float(str(row['votes']).replace(',', '')))
                        # time, actor, dan genre akan menjadi NULL (kosong)
                    )
                except (ValueError, TypeError):
                    continue

        self.stdout.write(self.style.SUCCESS('Database population complete!'))