from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Movie(models.Model):
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True, blank=True)
    description  = models.TextField()
    genres       = models.ManyToManyField(Genre, blank=True, related_name='movies')
    release_year = models.IntegerField()
    rating       = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    duration     = models.IntegerField(help_text="Duration in minutes")
    poster       = models.ImageField(upload_to='posters/')
    banner       = models.ImageField(upload_to='banners/', blank=True, null=True)
    video_file   = models.FileField(upload_to='videos/', blank=True, null=True)
    trailer_url  = models.URLField(blank=True, null=True, help_text="YouTube embed URL")
    is_featured  = models.BooleanField(default=False)
    is_trending  = models.BooleanField(default=False)
    views        = models.IntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def duration_display(self):
        hours   = self.duration // 60
        minutes = self.duration % 60
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def genre_name(self):
        return ', '.join(g.name for g in self.genres.all()) or 'Uncategorized'

    def genre_slug(self):
        first = self.genres.first()
        return first.slug if first else ''


class Review(models.Model):
    movie      = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    rating     = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


class Watchlist(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    movie    = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


class WatchHistory(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    movie      = models.ForeignKey(Movie, on_delete=models.CASCADE)
    progress   = models.IntegerField(default=0, help_text="Progress in seconds")
    watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"


# ── This function MUST be outside any class ──
def profile_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'profiles/{instance.user.username}.{ext}'


class Profile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    bio   = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_photo(self):
        if self.photo:
            return self.photo.url
        return None


# ── Auto-create Profile when User is created ──
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)