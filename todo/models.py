from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Todo(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField()
    created_in = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    column = models.CharField(max_length=50, default='column1')
    position = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    
    class Meta:
        ordering = ['column', 'position']
    
    def edit(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()

    def __str__(self):
        return self.title
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)