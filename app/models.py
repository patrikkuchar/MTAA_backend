from django.db import models

# Create your models here.
class User(models.Model):
  #id = models.BigAutoField(primary_key=True)
  name = models.CharField(max_length=100)
  surname = models.CharField(max_length=100)
  email= models.CharField(max_length=100)
  password = models.CharField(max_length=100)

  class Meta:
    db_table = "users"
