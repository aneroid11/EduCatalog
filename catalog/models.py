from django.db import models
from django.urls import reverse


class MyModel(models.Model):
    my_field = models.CharField(max_length=20, help_text="Enter field")

    class Meta:
        ordering = ['-my_field']

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.my_field
