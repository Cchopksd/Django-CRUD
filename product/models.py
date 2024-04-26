from django.db import models
from db_connection import db


collection = db["product"]

# class Seed(models.Model):
#     _id = models.IntegerField(primary_key=True)
#     Seed_RepDate = models.IntegerField()
#     Seed_Year = models.IntegerField()
#     Seeds_YearWeek = models.IntegerField()
#     Seed_Varity = models.CharField(max_length=50)
#     Seed_RDCSD = models.CharField(max_length=100)
#     Seed_Stock2Sale = models.CharField(max_length=50)
#     Seed_Season = models.IntegerField()
#     Seed_Crop_Year = models.CharField(max_length=10)
