from django.db import models

# Create your models here.
class User(models.Model):
  name = models.CharField(max_length=100)
  surname = models.CharField(max_length=100)
  email= models.CharField(max_length=100)
  password = models.CharField(max_length=100)

  class Meta:
    db_table = "users"

class Region(models.Model):
  name = models.CharField(max_length=255)

  class Meta:
    db_table = "regions"

class Subregion(models.Model):
  name = models.CharField(max_length=255)
  region = models.ForeignKey(Region, related_name="regions", blank=True, null=True, on_delete=models.SET_NULL)

  class Meta:
    db_table = "subregions"

class Property(models.Model):
  rooms = models.BigIntegerField()
  area = models.BigIntegerField()
  price = models.BigIntegerField()
  subregion = models.ForeignKey(Subregion, related_name="subregion", blank=True, null=True, on_delete=models.SET_NULL)
  last_updated = models.DateTimeField()
  owner = models.ForeignKey(User, related_name="userss", blank=True, null=True, on_delete=models.SET_NULL)
  address = models.CharField(max_length=255)
  info = models.TextField()

  class Meta:
    db_table = "properties"

class Booking(models.Model):
  #property_id = models.BigIntegerField()
  #buyer_id = models.BigIntegerField()

  property = models.ForeignKey(Property, related_name="properties", blank=True, null=True, on_delete=models.SET_NULL)
  buyer = models.ForeignKey(User, related_name="users", blank=True, null=True, on_delete=models.SET_NULL)
  time = models.DateTimeField()

  class Meta:
    db_table = "bookings"

class Image(models.Model):
  property = models.ForeignKey(Property, related_name="propertiess", blank=True, null=True, on_delete=models.SET_NULL)
  image_url = models.CharField(max_length=255)
  title = models.BooleanField()

  class Meta:
    db_table = "images"


class Liked(models.Model):
  property = models.ForeignKey(Property, related_name="propertiesa", blank=True, null=True, on_delete=models.SET_NULL)
  user = models.ForeignKey(User, related_name="usersa", blank=True, null=True, on_delete=models.SET_NULL)

  class Meta:
    db_table = "liked"