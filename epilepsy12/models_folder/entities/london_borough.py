"""
# Auto-generated `LayerMapping` dictionary for LondonBorough model
londonborough_mapping = {
    "name": "NAME",
    "gss_code": "GSS_CODE",
    "hectares": "HECTARES",
    "nonld_area": "NONLD_AREA",
    "ons_inner": "ONS_INNER",
    "sub_2009": "SUB_2009",
    "sub_2006": "SUB_2006",
    "geom": "MULTIPOLYGON",
}
"""

from django.contrib.gis.db import models


class LondonBoroughBoundaries(models.Model):
    name = models.CharField(max_length=22)
    gss_code = models.CharField(max_length=9)
    hectares = models.FloatField()
    nonld_area = models.FloatField()
    ons_inner = models.CharField(max_length=1)
    sub_2009 = models.CharField(max_length=7, null=True)
    sub_2006 = models.CharField(max_length=10, null=True)
    geom = models.MultiPolygonField(srid=27700)

    class Meta:
        abstract = True


class LondonBorough(LondonBoroughBoundaries):
    class Meta:
        indexes = [models.Index(fields=["gss_code"])]
        verbose_name = "London Borough"
        verbose_name_plural = "London Boroughs"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_gss_code(self) -> str:
        return self.gss_code
