print "i am monkeypatching top level models yow"
import django.db.backends.util                                                                                        
orig_typecast_date = django.db.backends.util.typecast_date                                                            
def monkeypatch_typecast_date(s):
    print "monkeypatch in effect son! Date is: %s" % s
    if s and 'T' in s:                                                                                                
        s = s[:s.find('T')]                                                                                           
    return orig_typecast_date(s)                                                                                      
django.db.backends.util.typecast_date = monkeypatch_typecast_date 