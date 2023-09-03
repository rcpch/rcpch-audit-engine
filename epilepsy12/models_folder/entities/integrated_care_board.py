from django.contrib.gis.db import models
from .integrated_care_board_boundaries import IntegratedCareBoardBoundaries


class IntegratedCareBoard(IntegratedCareBoardBoundaries):
    ods_code = models.CharField()

    class Meta:
        verbose_name = "Integrated Care Board"
        verbose_name_plural = "Integrated Care Boards"
        ordering = ("icb23nm",)

    def __str__(self) -> str:
        return self.icb23nm

    def get_ods_code(self) -> str:
        return self.ods_code
