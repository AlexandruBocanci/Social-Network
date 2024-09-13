from django.contrib import admin
from .models import Profile, Post, Like

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'bio', 'avatar', 'slug']
    prepopulated_fields = {'slug': ('user', 'date_of_birth')}  # Verifica daca slug-ul este generat corect

admin.site.register(Profile, ProfileAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'image', 'video', 'slug']
    exclude = ['created_at']  # Exclude 'created_at' din formularul admin

    prepopulated_fields = {'slug': ('user', 'content')}  # Ajusteaza campurile pentru slug

admin.site.register(Post, PostAdmin)

class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at', 'slug']
    prepopulated_fields = {'slug': ('user', 'post')}  # Verifica daca slug-ul este necesar pentru Like

admin.site.register(Like, LikeAdmin)
