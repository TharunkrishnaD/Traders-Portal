from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    scripcode = models.IntegerField()

    def __str__(self):
        return self.company_name

class WatchlistEntry(models.Model):
    user = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)