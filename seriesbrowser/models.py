from django.db import models

class Brain(models.Model):
    name = models.CharField(max_length=200)

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
    labelMethod = models.ForeignKey(LabelMethod)
    imageMethod = models.ForeignKey(ImageMethod)
    desc = models.CharField('description', max_length=200)
    brain = models.ForeignKey(Brain)
    lab = models.ForeignKey(Laboratory)
    isRestricted = models.BooleanField(default='false')
    sectionThickness = models.IntegerField()
    sectionThicknessUnit = models.CharField(max_length=2) 
    sectioningPlane = models.ForeignKey(SectioningPlane)
    pedagogicalUnit = models.ManyToManyField(PedagogicalUnit)
    numQCSections = models.IntegerField()
    #indicate sample section
    def __unicode__(self):
        return self.desc

class NearestSeries(models.Model):
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    series = models.ForeignKey(Series)
    nearestSeriesId = models.IntegerField(Series)

class Section(models.Model):
    series = models.ForeignKey(Series)
    name = models.CharField(max_length=200)
    sectionOrder = models.IntegerField()
    pngPathLow = models.CharField(max_length=200)
    pngPathHigh = models.CharField(max_length=200)
    jp2Path = models.URLField(verify_exists=False)
    jp2FileSize = models.BigIntegerField(null=True)
    jp2BitDepth = models.IntegerField(null=True)
    isSampleSection = models.BooleanField(default='false')
    y_coord = models.IntegerField(null=True)
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
    tracer = models.ForeignKey(Tracer)
    volume = models.DecimalField(max_digits=5, decimal_places=2)
    volumeUnits = models.CharField(max_length=2)
    x_coord = models.DecimalField(max_digits=3, decimal_places=2)
    y_coord = models.DecimalField(max_digits=3, decimal_places=2)
    z_coord = models.DecimalField(max_digits=3, decimal_places=2)
    #other atlas and injection fields

    def __unicode__(self):
        return "x:%.3f y:%.3f z:%.3f" % (self.x_coord, self.y_coord, self.z_coord)

class Updater(models.Model):
    name = models.CharField(max_length=200)
    lastLoggedIn = models.DateField()
    
    def __unicode__(self):
        return self.name


class SeriesNote(models.Model):
    series = models.ForeignKey(Series)
    updater = models.ForeignKey(Updater)
    score = models.IntegerField()
    comment = models.CharField(max_length=200)
    write_date = models.DateTimeField()

    def __unicode__(self):
        return self.comment

class SectionNote(models.Model):
    section = models.ForeignKey(Section)
    updater = models.ForeignKey(Updater)
    score = models.IntegerField()
    comment = models.CharField(max_length=200)
    write_date = models.DateTimeField()

    def __unicode__(self):
        return self.comment

