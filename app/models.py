from django.db import models

# Create your models here.
class User(models.Model):
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
  property = models.ForeignKey(Property, related_name="properties", blank=True, null=True, on_delete=models.SET_NULL)
  user = models.ForeignKey(User, related_name="users", blank=True, null=True,on_delete=models.SET_NULL)

  class Meta:
    db_table = "liked"