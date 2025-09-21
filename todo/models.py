from django.db import models
from django.utils import timezone

class Todo(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now, )
    duedate = models.DateField(null=True, blank=True)
    
    
    def edit(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()

    def __str__(self):
        return self.title