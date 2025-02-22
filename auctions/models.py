from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"

class Bid(models.Model):
    bid = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBids")

    def __str__(self):
        return f"{self.bid}"

class Listing(models.Model):
    title = models.CharField(max_length=108)
    description = models.TextField()
    imageUrl = models.CharField(max_length=1000)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bidPrice", default="0")
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userListing")
    category = models.ManyToManyField(Category, blank=True, related_name="categoryListing")
    watchlist = models.ManyToManyField(User, blank=True, related_name="userWatchlist")

    def __str__(self):
        return f"{self.title}"
    
    
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComments")
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComments")
     
    def __str__(self):
        return f"{self.comment}"