from django.contrib.gis.db import models
from .local_health_board_boundaries import LocalHealthBoardBoundaries


class LocalHealthBoard(LocalHealthBoardBoundaries):
    ods_code = models.CharField(max_length=3)

    class Meta:
        indexes = [models.Index(fields=["ods_code"])]
        verbose_name = "Local Health Board"
        verbose_name_plural = "Local Health Boards"
        ordering = ("lhb22nm",)

    def __str__(self) -> str:
        return self.lhb22nm

    def get_ods_code(self) -> str:
        return self.ods_code
