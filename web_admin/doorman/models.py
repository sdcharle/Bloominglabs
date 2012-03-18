from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


NOTIFICATION_TYPE_CHOICES = (
    ('Access', 'Door Unlocked'),
)

"""

some usage examples to save grief later.
prof = UserProfile.objects.get(rfid_slot = 1)

"""

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    # Other fields here
    rfid_access = models.BooleanField(default=False)
    rfid_tag = models.CharField(max_length=20,blank=True,null=True)
    rfid_slot = models.IntegerField(unique=True) # refers to slot in Open Access
# from this guy: http://stackoverflow.com/questions/2813189/django-userprofile-with-unique-foreign-key-in-django-admin
# need: mask(?)
# 0 or 255 means disabled or uninited.

    rfid_label = models.CharField(max_length = 50) # little label on the tag
    
    
    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.all().get(user=self.user)
            self.id = existing.id #force update instead of insert
        except UserProfile.DoesNotExist:
            pass 
        models.Model.save(self, *args, **kwargs)
    
# definition of UserProfile from above

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

"""

for storing when we let ppl in

"""

class AccessEvent(models.Model):
    user = models.ForeignKey(User) # profile?
    event_date = models.DateTimeField(auto_now = True)

"""

for storing things we sensed

"""

class SensorEvent(models.Model):
    event_type = models.CharField(max_length=50)
    event_source = models.CharField(max_length=50)
    event_date = models.DateTimeField(auto_now = True)
    event_value = models.CharField(max_length=20, blank=True, null = True)
    
"""

for notifications

"""

class PushingboxNotification(models.Model):
    notification_user = models.ForeignKey(User)
    notification_devid = models.CharField(max_length = 30)
    notification_type = models.CharField(max_length = 20, choices=NOTIFICATION_TYPE_CHOICES)