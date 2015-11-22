
//yo
#ifndef UserDB_h
#define UserDB_h
#include <inttypes.h>
#include <Arduino.h>
#include <EEPROM.h>
#define EEPROM_FIRSTUSER 24
#define EEPROM_LASTUSER 1024
#define NUMUSERS  ((EEPROM_LASTUSER - EEPROM_FIRSTUSER)/5)  //Define number of internal users (200 for UNO/Duemillanova)

class EEPROM_UserDB {
  
  public:
    void dumpUsers();
    void clearUsers();
    boolean upsertUser(byte userMask, unsigned long tagNumber);
    boolean deleteUser(unsigned long tagNumber);
    int checkUser(unsigned long tagNumber);
    int findUser(unsigned long tagNumber);
    void dumpUser(byte usernum);
    int getUserMask(unsigned long tagNumber);
        
};

//extern EEPROM_UserDB EEPROM_UserDB;

#endif
