from django.db import models

class UserWithAccess(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=24)
    chip_identifier = models.BinaryField(max_length=4)
    pass_code = models.CharField(max_length=4)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    event = models.CharField(max_length=63)
    message = models.TextField()
