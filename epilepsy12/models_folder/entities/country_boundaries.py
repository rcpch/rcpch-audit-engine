# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class CountryBoundaries(models.Model):
    ctry22cd = models.CharField(max_length=9)
    ctry22nm = models.CharField(max_length=16)
    ctry22nmw = models.CharField(max_length=17)
    bng_e = models.BigIntegerField()
    bng_n = models.BigIntegerField()
    long = models.FloatField()
    lat = models.FloatField()
    globalid = models.CharField(max_length=38)
    geom = models.MultiPolygonField(srid=27700)

    def __str__(self) -> str:
        return self.ctry22nm


"""
# Auto-generated `LayerMapping` dictionary for CountryBoundaries model
countryboundaries_mapping = {
    'ctry22cd': 'CTRY22CD',
    'ctry22nm': 'CTRY22NM',
    'ctry22nmw': 'CTRY22NMW',
    'bng_e': 'BNG_E',
    'bng_n': 'BNG_N',
    'long': 'LONG',
    'lat': 'LAT',
    'globalid': 'GlobalID',
    'geom': 'MULTIPOLYGON',
}
"""
