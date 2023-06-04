# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class NHSEnglandRegionBoundaries(models.Model):
    nhser22cd = models.CharField(max_length=9)
    nhser22nm = models.CharField(max_length=24)
    bng_e = models.BigIntegerField()
    bng_n = models.BigIntegerField()
    long = models.FloatField()
    lat = models.FloatField()
    globalid = models.CharField(max_length=38)
    geom = models.MultiPolygonField(srid=27700)


# Auto-generated `LayerMapping` dictionary for NHSEnglandRegionBoundaries model
# nhsenglandregionboundaries_mapping = {
#     "nhser22cd": "NHSER22CD",
#     "nhser22nm": "NHSER22NM",
#     "bng_e": "BNG_E",
#     "bng_n": "BNG_N",
#     "long": "LONG",
#     "lat": "LAT",
#     "globalid": "GlobalID",
#     "geom": "MULTIPOLYGON",
# }
