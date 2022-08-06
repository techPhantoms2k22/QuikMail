from django.db import models
from regex import F
# from regex import F

# Create your models here.
class userDB(models.Model):
    username = models.CharField(max_length=50,primary_key=True)
    first_name = models.CharField(max_length=50,null=False,default="userFirstName")
    last_name = models.CharField(max_length=50,null=False,default="userLastName")
    # private_key = models.CharField(max_length=1024,null=False,default="userPrivateKey")
    password = models.CharField(max_length=1024,null=False,default="userPassword")

    def __str__(self):
        return self.username