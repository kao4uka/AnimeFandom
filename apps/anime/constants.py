from django.db import models


class Status(models.TextChoices):
    NO_PUBLISH = 'NP', 'NoPublish'
    PUBLISHED = 'PB', 'Published'


GENDER = (
    ("Мужчина", "Мужчина"),
    ("Женщина", "Женщина"),
    ("Другое", "Другое"),
)

AGE_LIMIT = (
    (6, '6+'),
    (12, '12+'),
    (16, '16+'),
    (18, '18+')
)

CACHE_TIMEOUT = 3600

RATING = [(i, i) for i in range(1, 11)]