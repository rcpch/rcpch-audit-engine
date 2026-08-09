"""
# Auto-generated `LayerMapping` dictionary for LocalHealthBoardBoundaries model
localhealthboardboundaries_mapping = {
    'boundary_identifier': 'LHB22CD',
    'name': 'LHB22NM',
    'welsh_name': 'LHB22NMW',
    'bng_e': 'BNG_E',
    'bng_n': 'BNG_N',
    'long': 'LONG',
    'lat': 'LAT',
    'globalid': 'GlobalID',
    'geom': 'MULTIPOLYGON',
}
"""

from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import TimeStampAbstractBaseClass


class LocalHealthBoardBoundaries(TimeStampAbstractBaseClass):
    boundary_identifier = models.CharField(max_length=9)
    name = models.CharField(max_length=41)
    welsh_name = models.CharField(max_length=40)
    bng_e = models.FloatField(null=True, blank=True)
    bng_n = models.FloatField(null=True, blank=True)
    long = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    globalid = models.CharField(max_length=38, null=True, blank=True)
    geom = models.MultiPolygonField(srid=27700, null=True, blank=True)

    class Meta:
        abstract = True


class LocalHealthBoardManager(models.Manager):
    def get_local_health_board_list(self, exclude_pk=None):
        queryset = self.filter(active=True)

        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)

        return queryset.order_by("name")

class LocalHealthBoard(LocalHealthBoardBoundaries):
    objects = LocalHealthBoardManager()
    ods_code = models.CharField(max_length=3)
    publication_date = models.DateField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["ods_code"])]
        verbose_name = "Local Health Board"
        verbose_name_plural = "Local Health Boards"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_ods_code(self) -> str:
        return self.ods_code

    def get_publication_date(self) -> str:
        return self.publication_date
