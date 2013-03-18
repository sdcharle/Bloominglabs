from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from datetime import datetime
import settings
import rfid_sock

"""

Some considerations:
Asynchronous connection to Arduino/Board Firmware.

8/21/2012
oh fuck, now date format via sqlite is fucked. B/c updated outside Django?

Try in this order
1) all date manipulation - use datetime (or SQL Standard for comparing)
2) Move to postgres

Point to ponder:
Ideally, very few ppl will be in eeprom at all times. So just add a sync function?
In the future if you have 'add user at the reader with the special 'add user' tag, ensure that gets fed back to the django db.
ensure simple func to id stuff to sync, do periodically in the daemon process (twisted)

1/1/2013
Add rfid sock func

"""
   
NOTIFICATION_TYPE_CHOICES = (
    ('Access', 'Door Unlocked'),
)

"""

catch deletes for sync purposes

"""

def add_tag_to_delete_queue(tag):
    from django.db import connection, transaction
    cursor = connection.cursor()
    # Data modifying operation - commit required
    cursor.execute("insert into rfid_user_delete_queue (rfid_tag, delete_date) values (%s,%s)", [tag, datetime.now()])
    transaction.commit_unless_managed()

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    # Other fields here
    rfid_access = models.BooleanField(default=False)
    rfid_tag = models.CharField(max_length=20,blank=True,null=True,unique=True)
    #rfid_in_eeprom = models.BooleanField(default=False) # changed from slot, which was unwieldy to manage.

    rfid_label = models.CharField(max_length = 50) # little label on the tag
    update_date = models.DateTimeField(null=True, blank = False, auto_now = True) # taking matters into my own hands...
    sync_date = models.DateTimeField(null=True, blank=True)
    #syncing = models.IntegerField(default = 0)

    def save(self, *args, **kwargs):
        print "in da save, son"
        try:
            mask = 255 # actually this is the 'locked out' - 0 is the 'just log it'
            existing = UserProfile.objects.all().get(user=self.user)

            self.id = existing.id #force update instead of insert
            if (self.rfid_access):
                mask = 1
            print "going for the EEPROM mod"
            if rfid_sock.modify_user(settings.RFID_SERVER, settings.RFID_PORT, self.rfid_tag, mask, settings.RFID_PASSWORD):
                self.sync_date = datetime.now()
            # also set synch date, synching
            
        except UserProfile.DoesNotExist:
            pass 
        models.Model.save(self, *args, **kwargs) 
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# tie to User deletion
def profile_in_delete_queue(sender, instance, **kwargs):
    print "user about to be deleted, see if we need to put in queue"
    try:
        existing = UserProfile.objects.all().get(user=instance)
        if existing.rfid_tag:
            add_tag_to_delete_queue(existing.rfid_tag)
    except UserProfile.DoesNotExist:
        print "fuck, couldn't find profile for %s" % instance

post_save.connect(create_user_profile, sender=User)
pre_delete.connect(profile_in_delete_queue, sender=User)

"""

for storing when we let ppl in

"""

class AccessEvent(models.Model):
    user = models.ForeignKey(User) 
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

    add_date = models.DateTimeField(auto_now_add = True)
    update_date = models.DateTimeField(auto_now = True)    

"""

for when you're allowed in
(many to many to calendar)

"""

class Timespan(models.Model):
    
    name = models.CharField(max_length = 30)
    description = models.CharField(max_length = 100)
    sunday = models.BooleanField(default = False)
    monday = models.BooleanField(default = False)
    tuesday = models.BooleanField(default = False)
    wednesday = models.BooleanField(default = False)
    thursday = models.BooleanField(default = False)
    friday = models.BooleanField(default = False)
    saturday = models.BooleanField(default = False)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # ensure: end time after start time.
    
    add_date = models.DateTimeField(auto_now_add = True)
    update_date = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.name
    
"""

Assembly of timespans.

Many to Many to timespans
Many to Many to users

"""

class Calendar(models.Model):
    name = models.CharField(max_length = 30)
    description = models.CharField(max_length = 100)
    
    timespans = models.ManyToManyField(Timespan)
    groups = models.ManyToManyField(Group) # probably better to define groups and use them!
    
# should this relationship go in the user profile instead? 
    
    add_date = models.DateTimeField(auto_now_add = True)
    update_date = models.DateTimeField(auto_now = True)    

    # check to see if time falls in the calendar
    def in_calendar(self,check_date):
        # check time spans, once you get a hit, return true
        for t in self.timespans.all():
            if (t.monday and check_date.weekday == 0) or \
                (t.tuesday and check_date.weekday == 1) \
                (t.wednesday and check_date.weekday == 2) \
                (t.thursday and check_date.weekday == 3) \
                (t.friday and check_date.weekday == 4) \
                (t.saturday and check_date.weekday == 5) \
                (t.sunday and check_date.weekday == 6):
                    if check_date.time() > t.start_time and check_date.time() < t.end_time:
                        return True
        return False
                
    def __unicode__(self):
        return self.name
