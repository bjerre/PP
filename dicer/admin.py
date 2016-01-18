from django.contrib import admin
from dicer.models import Category, Page
from dicer.models import UserProfile
from dicer.models import Post



class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}



admin.site.register(Category, CategoryAdmin)
admin.site.register(Page)
admin.site.register(UserProfile)
admin.site.register(Post)


