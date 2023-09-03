# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class LocalHealthBoardBoundaries(models.Model):
    lhb22cd = models.CharField(max_length=9)
    lhb22nm = models.CharField(max_length=41)
    lhb22nmw = models.CharField(max_length=40)
    bng_e = models.FloatField()
    bng_n = models.FloatField()
    long = models.FloatField()
    lat = models.FloatField()
    globalid = models.CharField(max_length=38)
    geom = models.MultiPolygonField(srid=27700)

    class Meta:
        abstract = True


"""
# Auto-generated `LayerMapping` dictionary for LocalHealthBoardBoundaries model
localhealthboardboundaries_mapping = {
    'lhb22cd': 'LHB22CD',
    'lhb22nm': 'LHB22NM',
    'lhb22nmw': 'LHB22NMW',
    'bng_e': 'BNG_E',
    'bng_n': 'BNG_N',
    'long': 'LONG',
    'lat': 'LAT',
    'globalid': 'GlobalID',
    'geom': 'MULTIPOLYGON',
}
"""
