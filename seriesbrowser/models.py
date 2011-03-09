from django.db import models

class Series(models.Model):
	name = models.CharField(max_length=200)	
	#atlas and injection fields	

    	def __unicode__(self):
        	return self.name

class Section(models.Model):
    	FN_CHOICES = (
        	(u'F', u'Fluorescence'),
        	(u'N', u'Nissl'),
    	)

	series = models.ForeignKey(Series)
	name = models.CharField(max_length=200)	
	imaging = models.CharField(max_length=2, choices = FN_CHOICES)
	#atlas and injection fields	
	
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
