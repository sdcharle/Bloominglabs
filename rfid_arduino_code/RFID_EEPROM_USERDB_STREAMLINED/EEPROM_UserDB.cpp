/*

User database management (really should be factored out).

General plan is to have a UDB object.
Auth handled elsewhere

12/23/2012 SDC

12/31/2012 SDC
Have all serial messages here. Not a great idea. Should move in the future.

*/


#include "EEPROM_UserDB.h"

void EEPROM_UserDB::clearUsers()    //Erases all users from EEPROM
{
  for(int i=EEPROM_FIRSTUSER; i<=EEPROM_LASTUSER; i++){
    EEPROM.write(i,0xFF);   
  }
  Serial.println("All users cleared.");
}

// better user update. Take slots out of the picture altogether. Find empty slot and add
// or if tag is there, change mask
// or report: no empty slots, sorry charlie
boolean EEPROM_UserDB::upsertUser(byte userMask, unsigned long tagNumber) {
   int offset;// = EEPROM_FIRSTUSER; 
   byte EEPROM_buffer[5] ={0,0,0,0,0};  
   boolean foundEmpty = false;
   byte byteVal = 0;
   
   if (tagNumber > 0xffffffff || tagNumber < 0) {
      Serial.println("Tag Number must be between 0 and 0xFFFFFFFF. Ignored.");
      return false;
   }
   
   offset = findUser(tagNumber);
   
   if (offset >= 0) {
     Serial.print("Tag: ");
     Serial.print(tagNumber,HEX);
     EEPROM.write(offset+4, userMask);
     Serial.print(" found and updated to mask:");  
     Serial.println(userMask,DEC);
     return true;
   }
   // TODO, prob in following section
   // right place to start searching  
   offset = EEPROM_FIRSTUSER;

   while (!foundEmpty & (offset < EEPROM_LASTUSER)) {
      for (int i = 0; i < 5; i++) {
         if (EEPROM.read(offset + i) == 0xFF) {
           byteVal++;
         }
      } 

      if (byteVal == 5) {
        foundEmpty = true;
      } else {
        offset += 5;
        byteVal = 0; // reset
      }
   }
   
   if (offset < EEPROM_LASTUSER) {
        EEPROM_buffer[0] = byte(tagNumber &  0xFFF);   // Fill the buffer with the values to write to bytes 0..4 
        EEPROM_buffer[1] = byte(tagNumber >> 8);
        EEPROM_buffer[2] = byte(tagNumber >> 16);
        EEPROM_buffer[3] = byte(tagNumber >> 24);
        EEPROM_buffer[4] = byte(userMask);
        for(int i=0; i<5; i++){
          EEPROM.write((offset+i), (EEPROM_buffer[i])); // Store the resulting value in 5 bytes of EEPROM.
        }
        
        Serial.print("Tag: ");
        Serial.print(tagNumber,HEX);
        Serial.print(" successfully added with mask:");
        Serial.println(userMask,DEC);
        
     } else {
        Serial.println("Memory full, user not added."); 
     }
}
// took out old add user and delete user. I didn't like.
boolean EEPROM_UserDB::deleteUser(unsigned long tagNumber) {
   int offset = findUser(tagNumber); 
   if (offset >= 0) {
     for(int i=0; i<5; i++){
        EEPROM.write((offset+i), 0xFF); // Store the resulting value in 5 bytes of EEPROM.
                                                      // Starting at offset.
     }
     Serial.print("User deleted for tag: "); 
     Serial.println(tagNumber, HEX); //??? 
     return true;    
   } else {
     Serial.print("Tag: ");
     Serial.print(tagNumber, HEX);
     Serial.println(" not found, nothing to delete"); 
     return false;
   }
}

int EEPROM_UserDB::checkUser(unsigned long tagNumber)                                  // Check if a particular tag exists in the local database. Returns userMask if found.
{                                                                       // Users number 0..NUMUSERS
  // Find the first offset to check

  unsigned long EEPROM_buffer=0;                                         // Buffer for recreating tagNumber from the 4 stored bytes.
  int found=-1;

  for(int i=EEPROM_FIRSTUSER; i<=(EEPROM_LASTUSER-5); i=i+5){

    EEPROM_buffer=0;
    EEPROM_buffer=(EEPROM.read(i+3));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i+2));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i+1));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i));


    if((EEPROM_buffer == tagNumber) && (tagNumber !=0xFFFFFFFF) && (tagNumber !=0x0)) {    // Return a not found on blank (0xFFFFFFFF) entries 
      Serial.print("User ");
      Serial.print(((i-EEPROM_FIRSTUSER)/5),DEC);
      Serial.print(" authenticated ");
      found = EEPROM.read(i+4);
      Serial.print("with mask: ");
      Serial.println(found);
      return found;
    }                             

  }
  Serial.println("User not found");
  delay(1000);                                                            // Delay to prevent brute-force attacks on reader
  return found;                        
}

// Add for debugging. Show only user slots that have something.

// SDC version returns offset (if found - else -1. this makes checkin' it easy)
int EEPROM_UserDB::findUser(unsigned long tagNumber)                                  // Check if a particular tag exists in the local database. 
//Returns EEPROM offset if found.
{                                                                       // Users number 0..NUMUSERS
  // Find the first offset to check
  unsigned long EEPROM_buffer=0;                                         // Buffer for recreating tagNumber from the 4 stored bytes.

  for(int i=EEPROM_FIRSTUSER; i<=(EEPROM_LASTUSER-5); i=i+5){
    // note below  why XOR and not just plain old or 
    EEPROM_buffer=0;
    EEPROM_buffer=(EEPROM.read(i+3));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i+2));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i+1));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i));

    if((EEPROM_buffer == tagNumber) && (tagNumber !=0xFFFFFFFF) && (tagNumber !=0x0)) {    // Return a not found on blank (0xFFFFFFFF) entries 
      return i;
    }                             
  }
  return -1;                        
}


void EEPROM_UserDB::dumpUser(byte usernum)                                            // Return information ona particular entry in the local DB
{                                                                      // Users number 0..NUMUSERS

  unsigned long EEPROM_buffer=0;                                       // Buffer for recreating tagNumber from the 4 stored bytes.

  if((0<=usernum) && (usernum <=199)){
    int i=usernum*5+EEPROM_FIRSTUSER;
    int blankCount = 0;

    for (int b = 0; b < 5; b++) {
       if (EEPROM.read(i + b) == 0xFF) {
          blankCount++;
       } 
    }
    if (blankCount == 5) {
      Serial.print(((i-EEPROM_FIRSTUSER)/5),DEC);
      Serial.print("\t");
      Serial.print("UNUSED");
      return; // move along.... 
    }
    
    EEPROM_buffer=0;
    EEPROM_buffer=(EEPROM.read(i+3));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i+2));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i+1));
    EEPROM_buffer= EEPROM_buffer<<8;
    EEPROM_buffer=(EEPROM_buffer ^ EEPROM.read(i));

    Serial.print(((i-EEPROM_FIRSTUSER)/5),DEC);
    Serial.print("\t");
    Serial.print(EEPROM.read(i+4),DEC);
    Serial.print("\t");

    Serial.println(EEPROM_buffer,HEX);
  }
  else Serial.println("Bad user number!");
}

// look up based on tag no. - as always, -1 = not found
int EEPROM_UserDB::getUserMask(unsigned long tagNumber) {
   int offset = findUser(tagNumber);
   int mask = -1;
   if (offset >= 0) {
      mask = EEPROM.read(offset+4);
      Serial.print("Tag number: ");
      Serial.print(tagNumber,HEX);
      Serial.print(" user mask be: ");
      Serial.println(mask);
   } else {
      Serial.print("Tag number: ");
      Serial.print(tagNumber,HEX);
      Serial.println(" not found.");
   }   
   return mask;
}

void EEPROM_UserDB::dumpUsers() {
  for(int i=0; i<(NUMUSERS); i++){
    dumpUser(i);
  Serial.println();                                                   }
}
