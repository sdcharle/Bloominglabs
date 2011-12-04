"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import UserProfile
 
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
from models import UserProfile

# also could try (no 'fk_name') http://stackoverflow.com/questions/4565814/django-user-userprofile-and-admin


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    fk_name = 'user'
    max_num = 1
    
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline,]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

