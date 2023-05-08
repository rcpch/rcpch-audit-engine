# django
from django.contrib.gis.db import models

# 3rd party

# rcpch
# This is an auto-generated Django model module created by ogrinspect.


class IntegratedCareBoardBoundaries(models.Model):
    icb23cd = models.CharField(max_length=9)
    icb23nm = models.CharField(max_length=77)
    bng_e = models.BigIntegerField()
    bng_n = models.BigIntegerField()
    long = models.FloatField()
    lat = models.FloatField()
    globalid = models.CharField(max_length=38)
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self) -> str:
        return self.icb23nm


"""
# Auto-generated `LayerMapping` dictionary for IntegratedCareBoardBoundaries model
integratedcareboardboundaries_mapping = {
    'icb23cd': 'ICB23CD',
    'icb23nm': 'ICB23NM',
    'bng_e': 'BNG_E',
    'bng_n': 'BNG_N',
    'long': 'LONG',
    'lat': 'LAT',
    'globalid': 'GlobalID',
    'geom': 'MULTIPOLYGON',
}
"""
