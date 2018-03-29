from django.contrib import admin

from compare import models

admin.site.register(models.Item)
admin.site.register(models.Comparison)
admin.site.register(models.Tag)
admin.site.register(models.TaggedItem)