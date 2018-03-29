import os
import uuid
from random import randint

from django.db import models
from django.db.models.aggregates import Count

class ItemManager(models.Manager):
    '''Manager for Item'''
    def random(self):
        '''Returns a random Item'''
        count = self.aggregate(count = Count('uuid'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]

class Item(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    file = models.FileField(upload_to='uploads/', unique=True)
    place = models.IntegerField(default=9999999)
    objects = ItemManager()

    def __str__(self):
        return self.uuid.__str__() + ' - ' + self.file.name.__str__()

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    class Meta:
        ordering = ['file']

class Comparison(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    item_better = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'compare_item_better')
    item_worse = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'compare_item_worse')
    objects = models.Manager()

    def __str__(self):
        return self.uuid.__str__()

class Tag(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=32, unique=True)
    objects = models.Manager()

    def __str__(self):
        return self.name.__str__()

    class Meta:
        ordering = ['name']

class TaggedItem(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    objects = models.Manager()

    def __str__(self):
        return self.tag.__str__() + ' - ' + self.item.file.name.__str__()

    class Meta:
        ordering = ['tag']