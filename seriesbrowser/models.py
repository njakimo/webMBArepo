from django.db import models

class Series(models.Model):
	name = models.CharField(max_length=200)
	lab = models.CharField(max_length=200, default = 'mitra')

    	def __unicode__(self):
        	return self.name

class Injection(models.Model):
	series = models.ManyToManyField(Series)
        region = models.CharField(max_length=200)
        x = models.DecimalField(max_digits=3, decimal_places=2)
        y = models.DecimalField(max_digits=3, decimal_places=2)
        z = models.DecimalField(max_digits=3, decimal_places=2)
	#atlas and injection fields	

    	def __unicode__(self):
        	return self.region

class Section(models.Model):
	series = models.ForeignKey(Series)
	name = models.CharField(max_length=200)	
    	num = models.IntegerField()
	labelmethod = models.CharField(max_length=200)
	imagemethod = models.CharField(max_length=200)
	pngpath = models.CharField(max_length=200)
	jp2path = models.CharField(max_length=200)
	
    	def __unicode__(self):
        	return self.name

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
