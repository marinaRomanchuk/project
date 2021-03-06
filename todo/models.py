from django.db import models

# Create your models here.
class Todo(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    completed = models.BooleanField(default=False)
    start = models.DateField()
    end = models.DateField(blank=True)
    remind_me = models.BooleanField(default=True)


    def __str__(self):
        return self.title
