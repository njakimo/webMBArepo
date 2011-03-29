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
        return self.imageMethodname

class SectioningPlane(models.Model):
    desc = models.CharField('description', max_length=10)
    def __unicode__(self):
        return self.desc

class Series(models.Model):
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
        return self.name

class Section(models.Model):
    series = models.ForeignKey(Series)
    name = models.CharField(max_length=200)
    sectionOrder = models.IntegerField()
    labelMethod = models.ForeignKey(LabelMethod)
    imageMethod = models.ForeignKey(ImageMethod)
    pngPathLow = models.CharField(max_length=200)
    pngPathHigh = models.CharField(max_length=200)
    jp2Path = models.URLField(verify_exists=False)
    jp2FileSize = models.IntegerField()
    jp2BitDepth = models.IntegerField()
    isSampleSection = models.BooleanField(default='false')
    def __unicode__(self):
        return self.name

class Region(models.Model):
    code = models.CharField(max_length=5)
    desc = models.CharField('description', max_length=200)
    parentId = models.IntegerField()
    #other atlas and injection fields

    def __unicode__(self):
        return self.code

class Injection(models.Model):
    section = models.ForeignKey(Section)
    region = models.ForeignKey(Region)
    volume = models.DecimalField(max_digits=5, decimal_places=2)
    volumeUnits = models.CharField(max_length=2)
    x_coord = models.DecimalField(max_digits=3, decimal_places=2)
    y_coord = models.DecimalField(max_digits=3, decimal_places=2)
    z_coord = models.DecimalField(max_digits=3, decimal_places=2)
    #other atlas and injection fields

    def __unicode__(self):
        return "x:%.3f y:%.3f z:%.3f" % (self.x_coord, self.y_coord, self.z_coord)

class Tracer(models.Model):
    name = models.CharField(max_length=200)
    injection = models.ForeignKey(Injection)

    def __unicode__(self):
        return self.name


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

