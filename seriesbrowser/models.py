from django.db import models

class Brain(models.Model):
	name = models.CharField(max_length=200)

    	def __unicode__(self):
        	return self.name

class Target(models.Model):
        region = models.CharField(max_length=200)
        x = models.DecimalField(max_digits=3, decimal_places=2)
        y = models.DecimalField(max_digits=3, decimal_places=2)
        z = models.DecimalField(max_digits=3, decimal_places=2)
	lab = models.CharField(max_length=200)
	#atlas and injection fields	

    	def __unicode__(self):
        	return self.region

class Series(models.Model):
	brain = models.ForeignKey(Brain)
        injection = models.ForeignKey(Target, blank=True)
	name = models.CharField(max_length=200)
	labelmethod = models.CharField(max_length=200)
	imagemethod = models.CharField(max_length=200)

    	def __unicode__(self):
        	return self.name

class Section(models.Model):
	series = models.ForeignKey(Series)
	name = models.CharField(max_length=200)	
	
    	def __unicode__(self):
        	return self.name

class Thumbnail(models.Model):
    	QUALITY_CHOICES = (
        	(u'L', u'Low'),
        	(u'M', u'Medium'),
        	(u'H', u'High'),
    	)

	section = models.ForeignKey(Section)
	quality = models.CharField(max_length=2, choices = QUALITY_CHOICES)
	path = models.CharField(max_length=200)

    	def __unicode__(self):
        	return self.path

class Updater(models.Model):
	name = models.CharField(max_length=200)

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

class PedagogicalSection():
	section = models.ForeignKey(Section)	
    	url = models.CharField(max_length=200)

    	def __unicode__(self):
    	    return self.url
