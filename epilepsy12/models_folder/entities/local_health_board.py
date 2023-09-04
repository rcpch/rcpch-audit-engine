"""
# Auto-generated `LayerMapping` dictionary for LocalHealthBoardBoundaries model
localhealthboardboundaries_mapping = {
    'boundary_identifier': 'LHB22CD',
    'name': 'LHB22NM',
    'lhb22nmw': 'LHB22NMW',
    'bng_e': 'BNG_E',
    'bng_n': 'BNG_N',
    'long': 'LONG',
    'lat': 'LAT',
    'globalid': 'GlobalID',
    'geom': 'MULTIPOLYGON',
}
"""

from django.contrib.gis.db import models


class LocalHealthBoardBoundaries(models.Model):
    boundary_identifier = models.CharField(max_length=9)
    name = models.CharField(max_length=41)
    lhb22nmw = models.CharField(max_length=40)
    bng_e = models.FloatField()
    bng_n = models.FloatField()
    long = models.FloatField()
    lat = models.FloatField()
    globalid = models.CharField(max_length=38)
    geom = models.MultiPolygonField(srid=27700)

    class Meta:
        abstract = True


class LocalHealthBoard(LocalHealthBoardBoundaries):
    ods_code = models.CharField(max_length=3)

    class Meta:
        indexes = [models.Index(fields=["ods_code"])]
        verbose_name = "Local Health Board"
        verbose_name_plural = "Local Health Boards"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_ods_code(self) -> str:
        return self.ods_code
