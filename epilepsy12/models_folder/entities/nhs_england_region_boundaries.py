# django
from django.contrib.gis.db import models

# 3rd party

# rcpch


class NHSEnglandRegionBoundaries(models.Model):
    nhser20cd = models.CharField(max_length=9)
    nhser20nm = models.CharField(max_length=24)
    bng_e = models.BigIntegerField()
    bng_n = models.BigIntegerField()
    long = models.FloatField()
    lat = models.FloatField()
    globalid = models.CharField(max_length=38)
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self) -> str:
        return self.nhser20nm


"""
# Auto-generated `LayerMapping` dictionary for NHSEnglandRegionBoundaries model
nhsenglandregionboundaries_mapping = {
    'nhser20cd': 'nhser20cd',
    'nhser20nm': 'nhser20nm',
    'bng_e': 'bng_e',
    'bng_n': 'bng_n',
    'long': 'long',
    'lat': 'lat',
    'globalid': 'GlobalID',
    'geom': 'MULTIPOLYGON',
}
"""
