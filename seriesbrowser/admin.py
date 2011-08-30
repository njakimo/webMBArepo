from django.contrib import admin
from seriesbrowser.models import Brain, Series, Section, Injection, PedagogicalUnit

class BrainAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name',)
    readonly_fields =('name',)
admin.site.register(Brain, BrainAdmin)

def make_unrestricted(modeladmin, request, queryset):
    queryset.update(isRestricted=False)
    queryset.update(isReviewed=True)
    changelist_view = (request) 
make_unrestricted.short_description = "Unrestrict selected series"

def make_restricted(modeladmin, request, queryset):
    queryset.update(isRestricted=True)
make_restricted.short_description = "Restrict selected series"

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('desc', 'lab', 'numQCSections', 'admin_sample','admin_sections','isRestricted','isReviewed')
    list_filter = ('brain',)
    fields = ('desc', 'lab','numQCSections', 'admin_sample', 'sampleSection', 'admin_sections','isRestricted','isReviewed', 'pedagogicalUnit')
    readonly_fields =('desc', 'lab', 'numQCSections', 'admin_sample','admin_sections')
    actions = [make_restricted, make_unrestricted]
admin.site.register(Series, SeriesAdmin)

def make_invisible(modeladmin, request, queryset):
    queryset.update(isVisible=False)
make_invisible.short_description = "Hide selected sections"

def make_visible(modeladmin, request, queryset):
    queryset.update(isVisible=True)
make_visible.short_description = "Display selected sections"

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'series','y_coord', 'admin_thumbnail', 'admin_link','isVisible')
    list_filter = ('series',)
    fields = ('name', 'series','y_coord','admin_thumbnail', 'admin_link','isVisible')
    readonly_fields = ('name','series','y_coord','admin_thumbnail', 'admin_link')
    actions = [make_visible, make_invisible]
    ordering = ['y_coord']
admin.site.register(Section, SectionAdmin)

class InjectionAdmin(admin.ModelAdmin):
    list_display = ('series', 'x_coord','x_coord_actual','y_coord','y_coord_actual','z_coord','z_coord_actual','region','region_actual')
    fields = ('series','x_coord','x_coord_actual','y_coord','y_coord_actual','z_coord','z_coord_actual','region','region_actual')
    readonly_fields = ('series','x_coord','y_coord','z_coord')
admin.site.register(Injection, InjectionAdmin)

class PedagogicalUnitAdmin(admin.ModelAdmin):
    list_display = ('url',)
    fields = ('url',) 
admin.site.register(PedagogicalUnit, PedagogicalUnitAdmin)
