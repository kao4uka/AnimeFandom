from django.db import models
from django.db.models import Q


class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        queryset = self.get_queryset().filter(lookup).distinct()
        return queryset
