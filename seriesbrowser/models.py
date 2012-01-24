from django.db import models
from django.contrib.auth.models import User

class DataResolver(models.Model):
    identifier = models.CharField(max_length=200)
    imageFile = models.CharField(max_length=500)
    section = models.ForeignKey('Section')
    def __unicode__(self):
        return self.identifier

class Brain(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.name

class Laboratory(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

class PedagogicalUnit(models.Model):
    url = models.CharField(max_length=200)
    def __unicode__(self):
        return self.url

class BrainMethod(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        abstract = True

    def __unicode__(self):
     return self.name

class LabelMethod(BrainMethod):
    labelMethodName = models.CharField(max_length=200)

#    class Meta(BrainMethod.Meta):
#        db_table = 'seriesbrowser_label_method'  

    def __unicode__(self):
        return self.labelMethodName

class ImageMethod(BrainMethod):
    imageMethodName = models.CharField(max_length=200)

#    class Meta(BrainMethod.Meta):
#        db_table = 'seriesbrowser_label_method'  

    def __unicode__(self):
        return self.imageMethodName

class SectioningPlane(models.Model):
    desc = models.CharField('description', max_length=10)
    def __unicode__(self):
        return self.desc

class Series(models.Model):
    isAuxiliary = models.BooleanField(default=False)
    sampleSection = models.ForeignKey('Section', related_name='+', null=True)
    pixelResolution = models.FloatField(default=0.46)
    labelMethod = models.ForeignKey(LabelMethod)
    imageMethod = models.ForeignKey(ImageMethod)
    desc = models.CharField('description', max_length=200)
    brain = models.ForeignKey(Brain)
    lab = models.ForeignKey(Laboratory)
    isRestricted = models.BooleanField(default=True)
    sectionThickness = models.IntegerField()
    sectionThicknessUnit = models.CharField(max_length=2, default='um') 
    sectioningPlane = models.ForeignKey(SectioningPlane)
    pedagogicalUnit = models.ManyToManyField(PedagogicalUnit, blank=True, null=True)
    numQCSections = models.IntegerField(default=0)
    isReviewed = models.BooleanField(default=False)

    def admin_sample(self):
        return u'<img src="%s" />' % (self.sampleSection.pngPathLow)
    admin_sample.short_description = 'Sample'
    admin_sample.allow_tags = True

    def admin_sections(self):
        return '<a href="%s%s"> Sections' % ('http://mouse.brainarchitecture.org/admin/seriesbrowser/section/?series__id__exact=', str(self.id))
    admin_sections.short_description = 'SectionAdmin'
    admin_sections.allow_tags = True

    def __unicode__(self):
        return self.desc

class NearestSeries(models.Model):
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    series = models.ForeignKey(Series)
    nearestSeriesId = models.IntegerField(Series)

class Section(models.Model):
    isVisible = models.BooleanField(default=True)
    series = models.ForeignKey(Series)
    name = models.CharField(max_length=200)
    sectionOrder = models.IntegerField()
    pngPathLow = models.CharField(max_length=200)
    jp2Path = models.URLField(verify_exists=False)
    jp2FileSize = models.BigIntegerField(null=True)
    jp2BitDepth = models.IntegerField(null=True)
    y_coord = models.FloatField(null=True)

    def admin_thumbnail(self):
        return u'<img src="%s" />' % (self.pngPathLow)
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True

    def admin_link(self):
        return '<a href="%s/%s/%s/"> ViewerLink' % ('http://mouse.brainarchitecture.org/seriesbrowser/viewer', str(self.series.id), str(self.id))
    admin_link.short_description = 'Link'
    admin_link.allow_tags = True

    def __unicode__(self):
        return self.name

class Region(models.Model):
    desc = models.CharField('description', max_length=200)
    code = models.CharField(max_length=10)
    bamsMouseId = models.IntegerField()
    bamsRatId = models.IntegerField()
    parent = models.ForeignKey('Region')
    leftId = models.IntegerField()
    rightId = models.IntegerField()

    def descendant_ids(self):
        children = Region.objects.filter(leftId__gte=self.leftId, rightId__lte=self.rightId)
        return [child.id for child in children]

    def injection_count(self,auth=False):
        if auth:
            return Injection.objects.filter(region__id__in=self.descendant_ids()).count()
        else:
            return Injection.objects.filter(region__id__in=self.descendant_ids(),series__isRestricted=0).count()

    def generate_tree(self,expand=0,auth=False):
        tree = {'property' : { 'id' : self.id, 'name' : '%s (%d)' % (self.desc, self.injection_count(auth)) }}
        if expand > 0:
            tree['state'] = { 'open' : True }
            expand -= 1
        children = self.region_set.all()
        if children.count() > 0:
            tree['children'] = []
            for child in children:
                tree['children'].append(child.generate_tree(expand,auth))
        return tree

    def __unicode__(self):
        return "[%s] %s" % (self.code, self.desc)

class Tracer(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.name

class Injection(models.Model):
    series = models.ForeignKey(Series)
    region = models.ForeignKey(Region)
    region_actual = models.ForeignKey(Region, null=True, related_name='+')
    tracer = models.ForeignKey(Tracer)
    volume = models.DecimalField(max_digits=5, decimal_places=2)
    volumeUnits = models.CharField(max_length=2)
    x_coord = models.DecimalField(max_digits=3, decimal_places=2)
    y_coord = models.DecimalField(max_digits=3, decimal_places=2)
    z_coord = models.DecimalField(max_digits=3, decimal_places=2)
    x_coord_actual = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    y_coord_actual = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    z_coord_actual = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    #other atlas and injection fields

    def __unicode__(self):
        return "x:%.3f y:%.3f z:%.3f" % (self.x_coord, self.y_coord, self.z_coord)

class Updater(models.Model):
    name = models.CharField(max_length=200)
    lastLoggedIn = models.DateField()
    
    def __unicode__(self):
        return self.name


class SeriesAnnotation(models.Model):
    series = models.ForeignKey(Series)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s (%s)" % (self.series.desc, self.user.get_full_name())

class SectionAnnotation(models.Model):
    section = models.ForeignKey(Section)
    user = models.ForeignKey(User)
    isInjection = models.BooleanField(default=False)
    isLabeled = models.BooleanField(default=False)
    hemisphere = models.CharField(max_length=6, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.section.name, self.user.get_full_name())


class CommentType(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class SectionComment(models.Model):
    annotation = models.ForeignKey(SectionAnnotation)
    type = models.ForeignKey(CommentType)
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return "%s (%s) - %s" % (self.annotation.section.name, self.annotation.user.get_full_name(), self.type.name)

class SeriesComment(models.Model):
    annotation = models.ForeignKey(SeriesAnnotation)
    type = models.ForeignKey(CommentType)
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return "%s (%s) - %s" % (self.annotation.series.desc, self.annotation.user.get_full_name(), self.type.name)

