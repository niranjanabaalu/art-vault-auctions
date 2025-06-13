from django.db import models
from django.utils.timezone import now, make_aware
from pytz import timezone  # Ensure pytz is installed and imported
from django.contrib.auth.models import User
from django.utils import timezone
import pytz
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models


# Indian Standard Time (IST) timezone
IST = pytz.timezone('Asia/Kolkata')

class Painting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    price_range = models.CharField(max_length=100, verbose_name="Price Range")
    start_time = models.DateTimeField(verbose_name="Auction Start Time")
    end_time = models.DateTimeField(verbose_name="Auction End Time")
    picture = models.ImageField(upload_to='paintings/', verbose_name="Painting Picture")
    details = models.TextField(verbose_name="Additional Details")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notified = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_paintings')
    status = models.CharField(max_length=20, choices=[('Passed', 'Passed'), ('Sold', 'Sold')], default='Passed')
    payment_email_sent = models.BooleanField(default=False)
    

    def __str__(self):
        return self.title

    def is_upcoming(self):
        # Adjust time to Indian Standard Time
        start_time_ist = self.start_time.astimezone(IST)
        return start_time_ist > timezone.now()

    def time_left(self):
        # Adjust time to Indian Standard Time
        start_time_ist = self.start_time.astimezone(IST)
        if start_time_ist > timezone.now():
            return start_time_ist - timezone.now()
        return None

    def start_time_in_ist(self):
        # Converts the start time to IST without altering the actual database value
        start_time_ist = self.start_time.astimezone(IST)
        return start_time_ist.strftime('%I:%M %p')  # Format time as 12-hour format with AM/PM

    def end_time_in_ist(self):
        # Converts the end time to IST without altering the actual database value
        end_time_ist = self.end_time.astimezone(IST)
        return end_time_ist.strftime('%I:%M %p')  # Format time as 12-hour format with AM/PM
    
    def is_sold(self):
        if self.end_time < now():
            highest_bid = Bid.objects.filter(painting=self).order_by('-amount').first()  # Ensure this is initialized

        if highest_bid:  # Ensure highest_bid is not None
            if not self.sold:  # Only update if not already marked as sold
                self.sold = True
                self.status = "Sold"
                self.winner = highest_bid.user
                self.current_price = highest_bid.amount
                self.save(update_fields=["sold", "status", "winner", "current_price"])
            return True
        return False





class Bid(models.Model):
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    
class Transaction(models.Model):
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_as_seller')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_as_buyer')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    admin_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')])
    date = models.DateTimeField(auto_now_add=True)

    def calculate_commission(self):
        return self.amount_paid * self.admin_fee

    def total_payment(self):
        return self.amount_paid - self.calculate_commission()

    def __str__(self):
        return f"Transaction {self.id} - {self.painting.title}"
        
    
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=[('Light', 'Light'), ('Dark', 'Dark')], default='Light')

    def __str__(self):
        return f"Settings for {self.user.username}"
    
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(upload_to="profile_pics/", default="default.jpg", null=True, blank=True)

# Automatically create a profile for new users
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """ Automatically create a profile when a user is created """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """ Save the profile every time the user is updated """
    instance.profile.save()


    
class Follower(models.Model):
    user = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follower')  # Prevent duplicate follows

    def __str__(self):
        return f"{self.follower.username} follows {self.user.username}"
    
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class AdminPainting(models.Model):
    """Model for paintings uploaded by the admin for direct sale."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    picture = models.ImageField(upload_to='admin_paintings/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 🛒 **Shopping Cart Model**
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    painting = models.ForeignKey(AdminPainting, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.painting.title} ({self.quantity})"

# 📦 **Order Model**
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending Payment', 'Pending Payment'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    painting = models.ForeignKey(AdminPainting, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Payment')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.painting.title} by {self.user.username}"