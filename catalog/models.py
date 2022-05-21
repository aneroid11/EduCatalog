from django.db import models
# from django.urls import reverse


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="For example, Science Fiction or Horror")

    def __str__(self):
        return self.name
