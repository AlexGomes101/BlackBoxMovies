from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.db.models import Q
from .models import Movie, Review, Watchlist, WatchHistory, Genre, Profile
import os, re


# ── Video streaming with range request support ──────────────
def _file_iterator(path, offset=0, length=None, chunk=8192):
    with open(path, 'rb') as f:
        f.seek(offset)
        remaining = length
        while True:
            read_size = chunk if remaining is None else min(chunk, remaining)
            data = f.read(read_size)
            if not data:
                break
            yield data
            if remaining is not None:
                remaining -= len(data)
                if remaining <= 0:
                    break


def stream_video(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    if not movie.video_file:
        return HttpResponse(status=404)

    video_path  = movie.video_file.path
    file_size   = os.path.getsize(video_path)
    content_type = 'video/mp4'
    range_header = request.META.get('HTTP_RANGE', '').strip()

    if not range_header:
        response = StreamingHttpResponse(_file_iterator(video_path), content_type=content_type, status=200)
        response['Content-Length'] = file_size
        response['Accept-Ranges']  = 'bytes'
        return response

    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        return HttpResponse(status=416)

    first_byte = int(range_match.group(1))
    last_byte  = int(range_match.group(2)) if range_match.group(2) else file_size - 1
    last_byte  = min(last_byte, file_size - 1)
    chunk_size = last_byte - first_byte + 1

    response = StreamingHttpResponse(
        _file_iterator(video_path, offset=first_byte, length=chunk_size),
        content_type=content_type, status=206
    )
    response['Content-Length'] = chunk_size
    response['Content-Range']  = f'bytes {first_byte}-{last_byte}/{file_size}'
    response['Accept-Ranges']  = 'bytes'
    return response


# ── Pages ────────────────────────────────────────────────────
def home(request):
    featured  = Movie.objects.filter(is_featured=True).first()
    trending  = Movie.objects.filter(is_trending=True)[:12]
    latest    = Movie.objects.all()[:12]
    top_rated = Movie.objects.order_by('-rating')[:12]
    genres    = Genre.objects.all()
    return render(request, 'movies/home.html', {
        'featured': featured, 'trending': trending,
        'latest': latest, 'top_rated': top_rated, 'genres': genres,
    })


def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    movie.views += 1
    movie.save(update_fields=['views'])

    similar = Movie.objects.filter(genres__in=movie.genres.all()).exclude(id=movie.id).distinct()[:6]
    reviews     = movie.reviews.all()[:10]
    user_review = None
    in_watchlist = False

    if request.user.is_authenticated:
        user_review  = Review.objects.filter(movie=movie, user=request.user).first()
        in_watchlist = Watchlist.objects.filter(movie=movie, user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        rating  = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        if rating:
            Review.objects.update_or_create(
                movie=movie, user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, 'Review submitted!')
            return redirect('movie_detail', slug=slug)

    return render(request, 'movies/detail.html', {
        'movie': movie, 'similar': similar, 'reviews': reviews,
        'user_review': user_review, 'in_watchlist': in_watchlist,
    })


def watch_movie(request, slug):
    if not request.user.is_authenticated:
        messages.warning(request, '🔒 Please sign in to watch movies.')
        return redirect(f'/login/?next=/watch/{slug}/')
    movie = get_object_or_404(Movie, slug=slug)
    WatchHistory.objects.get_or_create(user=request.user, movie=movie)
    return render(request, 'movies/watch.html', {'movie': movie})


def genre_view(request, genre_slug):
    genre  = get_object_or_404(Genre, slug=genre_slug)
    movies = Movie.objects.filter(genres=genre)
    genres = Genre.objects.all()
    return render(request, 'movies/genre.html', {
        'movies': movies, 'genre_name': genre.name,
        'genre': genre_slug, 'genres': genres,
    })


def search_view(request):
    query  = request.GET.get('q', '')
    movies = []
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})


def search_ajax(request):
    query   = request.GET.get('q', '')
    results = []
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) | Q(genres__name__icontains=query)
        ).distinct()[:8]
        for m in movies:
            results.append({
                'title':  m.title,
                'slug':   m.slug,
                'genre': m.genre_name(),
                'poster': m.poster.url if m.poster else '',
                'year':   m.release_year,
            })
    return JsonResponse({'results': results})


@login_required
def toggle_watchlist(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    obj, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


@login_required
def my_watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user).select_related('movie')
    return render(request, 'movies/watchlist.html', {'watchlist': watchlist})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to BlackBox, {user.username}!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'movies/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'movies/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
            profile.save()
            messages.success(request, '✅ Profile photo updated!')
            return redirect('profile')
        if 'bio' in request.POST:
            profile.bio = request.POST.get('bio', '')
            profile.save()
            messages.success(request, '✅ Bio updated!')
            return redirect('profile')

    history   = WatchHistory.objects.filter(user=request.user).select_related('movie')[:12]
    watchlist = Watchlist.objects.filter(user=request.user).select_related('movie')[:12]
    return render(request, 'movies/profile.html', {
        'history': history, 'watchlist': watchlist, 'profile': profile,
    })