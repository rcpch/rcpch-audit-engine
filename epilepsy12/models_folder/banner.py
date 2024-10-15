from django.db import models

class Banner(models.Model):
    url_matcher = models.CharField(max_length=255)
    html = models.TextField()

    def __str__(self):
        return f"Banner for {self.url_matcher}"