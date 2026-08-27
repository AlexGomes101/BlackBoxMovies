# blackbox/movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('watch/<slug:slug>/', views.watch_movie, name='watch_movie'),
    path('stream/<slug:slug>/', views.stream_video, name='stream_video'),  # ← ADD THIS
    path('genre/<slug:genre_slug>/', views.genre_view, name='genre'),
    path('search/', views.search_view, name='search'),
    path('search/ajax/', views.search_ajax, name='search_ajax'),
    path('watchlist/', views.my_watchlist, name='watchlist'),
    path('watchlist/toggle/<slug:slug>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]


# blackbox/blackbox/urls.py  (main project urls)
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('movies.urls')),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
