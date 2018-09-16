from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    search_history = ArrayField(
        ArrayField(
            models.CharField(max_length=50),
            size = 2,
            ),
        size = 5,
        )
    current_city = models.CharField(max_length = 30, blank=True)

    def add_to_history(self, query):
        self.search_history = [query] + self.search_history[:-1]