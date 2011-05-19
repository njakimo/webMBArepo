from django.contrib import admin
from seriesbrowser.models import Series, Section, Injection

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('desc', 'lab','isRestricted', 'numQCSections')
    fields = ('desc', 'lab','isRestricted', 'numQCSections')
    readonly_fields =('desc', 'lab', 'numQCSections')  
admin.site.register(Series, SeriesAdmin)

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'series','isSampleSection') 
    list_filter = ('series',)
    fields = ('name', 'series','isSampleSection') 
    readonly_fields = ('name', 'series') 
admin.site.register(Section, SectionAdmin)

class InjectionAdmin(admin.ModelAdmin):
    list_display = ('series', 'x_coord','y_coord','z_coord','region')
    fields = ('series','x_coord','y_coord','z_coord','region')
    readonly_fields = ('series','x_coord','y_coord','z_coord')
admin.site.register(Injection, InjectionAdmin)
