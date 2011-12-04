from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    # Other fields here
    rfid_access = models.BooleanField(default=False)
    rfid_tag = models.CharField(max_length=20,blank=True,null=True)
    rfid_slot = models.IntegerField(blank=True,null=True) # refers to slot in Open Access
# from this guy: http://stackoverflow.com/questions/2813189/django-userprofile-with-unique-foreign-key-in-django-admin

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
