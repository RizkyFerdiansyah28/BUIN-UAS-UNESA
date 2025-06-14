from django.db import models

# Tabel Dimensi untuk Genre
class DimGenre(models.Model):
    """
    Tabel dimensi yang menyimpan informasi unik tentang genre film.
    """
    genre_name = models.CharField(max_length=100, unique=True, help_text="Nama genre")

    def __str__(self):
        return self.genre_name

# Tabel Dimensi untuk Aktor
class DimActor(models.Model):
    """
    Tabel dimensi yang menyimpan informasi unik tentang aktor.
    """
    actor_name = models.CharField(max_length=255, unique=True, help_text="Nama aktor")

    def __str__(self):
        return self.actor_name

# Tabel Dimensi untuk Waktu (berdasarkan tahun rilis)
class DimTime(models.Model):
    """
    Tabel dimensi yang menyimpan informasi tentang tahun rilis.
    """
    release_year = models.IntegerField(unique=True, help_text="Tahun rilis film")

    def __str__(self):
        return str(self.release_year)

# Tabel Fakta untuk Film
class FactMovie(models.Model):
    """
    Tabel fakta yang menjadi pusat skema, menghubungkan semua dimensi
    dan menyimpan metrik utama seperti rating dan jumlah suara.
    """
    # Kolom untuk foreign key ke tabel dimensi
    genre = models.ForeignKey(DimGenre, on_delete=models.SET_NULL, null=True)
    actor = models.ForeignKey(DimActor, on_delete=models.SET_NULL, null=True)
    time = models.ForeignKey(DimTime, on_delete=models.SET_NULL, null=True)

    # Metrik atau fakta yang diukur
    title = models.CharField(max_length=255, help_text="Judul film")
    rating = models.FloatField(help_text="Rating film")
    votes = models.IntegerField(help_text="Jumlah suara yang diberikan untuk film")
    actor_appearance_count = models.IntegerField(default=0, help_text="Jumlah kemunculan aktor dalam satu tahun")
    genre_appearance_count = models.IntegerField(default=0, help_text="Jumlah kemunculan genre dalam satu tahun")

    def __str__(self):
        return self.title