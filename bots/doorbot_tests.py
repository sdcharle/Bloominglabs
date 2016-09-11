"""

Speed the testing pilgrim

9/8/2016 SDC

"""


from django.db import models
from doorman.models import UserProfile, AccessEvent, SensorEvent, PushingboxNotification
from django.contrib.auth.models import User

prfo = UserProfile.objects.get(rfid_tag__iexact = 'shit')
