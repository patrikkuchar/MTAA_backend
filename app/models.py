from MySQLdb import Timestamp
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


class Property(models.Model):
  rooms = models.BigIntegerField()
  area = models.BigIntegerField()
  price = models.BigIntegerField()
  region = models.CharField(max_length=255)
  subregion = models.CharField(max_length=255)
  last_updated = models.DateTimeField()
  owner_id = models.BigIntegerField()
  address = models.CharField(max_length=255)
  info = models.TextField()

  class Meta:
    db_table = "properties"

class Booking(models.Model):
  property_id = models.BigIntegerField()
  buyer_id = models.BigIntegerField()
  time = models.DateTimeField()

  class Meta:
    db_table = "bookings"

class Image(models.Model):
  property_id = models.BigIntegerField()
  image_url = models.CharField(max_length=255)

  class Meta:
    db_table = "images"


class Liked(models.Model):
  property_id = models.BigIntegerField()
  user_id = models.BigIntegerField()

  class Meta:
    db_table = "liked"