"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import UserProfile
# sdc 6/24/2015

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
	model = UserProfile

class UserProfileAdmin(UserAdmin):
	inlines = [UserProfileInline]

admin.site.register(User, UserProfileAdmin)
"""

"""

note-

the below plus overriding userprofile save (see models)
is the only thing that fixed the 'non-unique id' bullshit


From this guy

"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from models import UserProfile, AccessEvent, SensorEvent, PushingboxNotification, Timespan, Calendar
from django.contrib.admin import SimpleListFilter


class RFIDFilter(SimpleListFilter):
    title = 'Has RFID access'
    parameter_name = 'rfid_access'

    def lookups(self, request, model_admin):
        return (
                 ('Yes', 'Yes'),
                 ('No', 'No'),
               )

    def queryset(self, request, queryset):
        """
        filter be access
        """
        if self.value() == 'Yes':
            return queryset.filter(userprofile__rfid_access__exact = True)
        if self.value() == 'No':
            return queryset.filter(userprofile__rfid_access__exact = False)

# also could try (no 'fk_name') http://stackoverflow.com/questions/4565814/django-user-userprofile-and-admin

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    #exclude = ('sync_date',)
    fk_name = 'user'
    max_num = 1


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline,]
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'user_rfid_access',  'user_rfid_tag', 'user_rfid_label',
                    'user_sync_date', 'is_active')
    list_filter = (RFIDFilter,)

    def user_rfid_tag(self, instance):
        return instance.get_profile().rfid_tag

    def user_rfid_label(self, instance):
        return instance.get_profile().rfid_label

    def user_rfid_access(self, instance):
        return instance.get_profile().rfid_access

    def user_sync_date(self, instance):
        return instance.get_profile().sync_date

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class AccessEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_date')

admin.site.register(AccessEvent, AccessEventAdmin)

class SensorEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_source', 'event_date', 'event_value')

admin.site.register(SensorEvent, SensorEventAdmin)

class PushingboxNotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_user', 'notification_type', 'notification_devid',)

admin.site.register(PushingboxNotification, PushingboxNotificationAdmin)


class TimespanAdmin(admin.ModelAdmin):
    pass

admin.site.register(Timespan, TimespanAdmin)

class CalendarAdmin(admin.ModelAdmin):
    filter_horizontal = ('timespans', 'groups',)


admin.site.register(Calendar, CalendarAdmin)
