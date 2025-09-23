from django.db import models
from django.utils import timezone


class Todo(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField()
    created_in = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    column = models.CharField(max_length=50, default='column1')  # coluna1, coluna2, etc.
    position = models.IntegerField(default=0)  # Ordem dentro da coluna
    
    class Meta:
        ordering = ['column', 'position']
    
    def edit(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()

    def __str__(self):
        return self.title