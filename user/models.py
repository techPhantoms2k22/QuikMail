from django.db import models
from regex import F
# from regex import F

# Create your models here.
class userDatabase(models.Model):
    username = models.CharField(max_length=50,primary_key=True)
    firstName = models.CharField(max_length=50,null=False,default="userFirstName")
    lastName = models.CharField(max_length=50,null=False,default="userLastName")
    dateOfBirth = models.DateField(auto_now=False)
    phoneNumber = models.CharField(max_length=10)

    def __str__(self):
        return self.username
