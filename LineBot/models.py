from django.db import models

# Create your models here.
# class User(models.Model):
#     uid = 
#     line_name =
#     pic_url = 

class User(models.Model):
    user_id = models.CharField(max_length=25, unique=True)
    user_name = models.CharField(max_length=255)
    line_name = models.CharField(max_length=255)
    pic_url = models.URLField()
    department = models.CharField(max_length=255)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)

class Group(models.Model):
    company = models.CharField(max_length=255)
    number = models.IntegerField()