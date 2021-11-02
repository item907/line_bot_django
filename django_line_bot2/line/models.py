from django.db import models

# Create your models here.
class TextChat(models.Model):
    keyword = models.CharField(max_length = 20, null = False)
    chatword = models.CharField(max_length = 1000, null = False)
    isword = models.BooleanField(default = True)
    
    def __str__(self):
        return self.keyword