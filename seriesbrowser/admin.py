from django.contrib import admin
from seriesbrowser.models import Series, Section, Injection

admin.site.register(Series)
admin.site.register(Section)

class InjectionAdmin(admin.ModelAdmin):
    list_display = ('x_coord','y_coord','z_coord','region')
    fields = ('x_coord','y_coord','z_coord','region')
    readonly_fields = ('x_coord','y_coord','z_coord')
admin.site.register(Injection, InjectionAdmin)