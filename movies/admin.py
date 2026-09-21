from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Sum, Avg
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Movie, Review, Watchlist, WatchHistory, Genre, Profile

admin.site.site_header  = "BlackBox Movies Admin"
admin.site.site_title   = "BlackBox Admin"
admin.site.index_title  = "Dashboard"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'movie_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name',)

    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'Movies'


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display       = ('title', 'get_genres', 'release_year', 'rating', 'get_watch_time', 'get_views', 'is_featured', 'is_trending')
    list_filter        = ('genres', 'is_featured', 'is_trending', 'release_year')
    search_fields      = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_display_links = ('title',)
    ordering           = ('-created_at',)
    readonly_fields    = ('watch_time_summary',)

    def get_genres(self, obj):
        return ', '.join(g.name for g in obj.genres.all())
    get_genres.short_description = 'Genres'

    def get_views(self, obj):
        return format_html('<span style="color:#e63946;font-weight:600">👁 {}</span>', obj.views)
    get_views.short_description = 'Views'

    def get_watch_time(self, obj):
        total   = WatchHistory.objects.filter(movie=obj).aggregate(t=Sum('progress'))['t'] or 0
        hours   = total // 3600
        minutes = (total % 3600) // 60
        if hours > 0:
            return format_html('<span style="color:#f0b429;font-weight:600">⏱ {}h {}m</span>', hours, minutes)
        return format_html('<span style="color:#f0b429;font-weight:600">⏱ {}m</span>', minutes)
    get_watch_time.short_description = 'Total Watch Time'

    def watch_time_summary(self, obj):
        qs      = WatchHistory.objects.filter(movie=obj)
        total   = qs.aggregate(t=Sum('progress'))['t'] or 0
        viewers = qs.count()
        avg     = qs.aggregate(a=Avg('progress'))['a'] or 0
        hours   = total // 3600
        minutes = (total % 3600) // 60
        avg_m   = int(avg) // 60
        return format_html('''
            <div style="
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                border: 1px solid #e63946;
                border-radius: 10px;
                padding: 20px 24px;
                display: flex;
                gap: 40px;
                flex-wrap: wrap;
                margin-top: 8px;
            ">
                <div style="text-align:center">
                    <div style="color:#e63946;font-size:1.8rem;font-weight:700">{}h {}m</div>
                    <div style="color:#aaa;font-size:0.78rem;margin-top:4px;text-transform:uppercase;letter-spacing:.08em">Total Watch Time</div>
                </div>
                <div style="text-align:center">
                    <div style="color:#f0b429;font-size:1.8rem;font-weight:700">{}</div>
                    <div style="color:#aaa;font-size:0.78rem;margin-top:4px;text-transform:uppercase;letter-spacing:.08em">Total Viewers</div>
                </div>
                <div style="text-align:center">
                    <div style="color:#00cec9;font-size:1.8rem;font-weight:700">{}m</div>
                    <div style="color:#aaa;font-size:0.78rem;margin-top:4px;text-transform:uppercase;letter-spacing:.08em">Avg Watch Time</div>
                </div>
                <div style="text-align:center">
                    <div style="color:#a29bfe;font-size:1.8rem;font-weight:700">{}</div>
                    <div style="color:#aaa;font-size:0.78rem;margin-top:4px;text-transform:uppercase;letter-spacing:.08em">Total Views</div>
                </div>
            </div>
        ''', hours, minutes, viewers, avg_m, obj.views)
    watch_time_summary.short_description = 'Watch Time Summary'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, f'✅ "{obj.title}" has been updated successfully.', messages.SUCCESS)
        else:
            self.message_user(request, f'🎬 "{obj.title}" has been added to BlackBox Movies!', messages.SUCCESS)

    def delete_model(self, request, obj):
        title = obj.title
        super().delete_model(request, obj)
        self.message_user(request, f'🗑️ "{title}" has been permanently deleted.', messages.WARNING)

    def delete_queryset(self, request, queryset):
        count  = queryset.count()
        titles = ', '.join(queryset.values_list('title', flat=True)[:3])
        super().delete_queryset(request, queryset)
        self.message_user(
            request,
            f'🗑️ {count} movie(s) deleted: {titles}{"..." if count > 3 else ""}',
            messages.WARNING
        )

    fieldsets = (
        ('Movie Info', {
            'fields': ('title', 'slug', 'description', 'genres', 'release_year', 'rating', 'duration')
        }),
        ('Media', {
            'fields': ('poster', 'banner', 'video_file', 'trailer_url')
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_trending')
        }),
        ('Statistics', {
            'fields': ('views',),
            'description': 'Manually adjust the view count if needed'
        }),
        ('Analytics', {
            'fields': ('watch_time_summary',),
            'description': 'Live watch statistics for this movie'
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter  = ('rating',)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display  = ('user', 'movie', 'get_progress', 'watched_at')
    list_filter   = ('movie',)
    search_fields = ('user__username', 'movie__title')

    def get_progress(self, obj):
        m = obj.progress // 60
        s = obj.progress % 60
        return format_html('<span style="color:#f0b429">{}m {}s</span>', m, s)
    get_progress.short_description = 'Progress'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_photo')

    def has_photo(self, obj):
        return '✅' if obj.photo else '❌'
    has_photo.short_description = 'Has Photo'


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display       = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_display_links = ('username',)

 