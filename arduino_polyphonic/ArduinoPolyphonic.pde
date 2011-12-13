/*

Arduino Polyphony!

A mash-up of the Cornell Kids' IR Harp (ORIG for ATmega644) and some code to play 
wav files w/ an AD5330 DAC.

12/10/2011

NOTE, SDC heavily modified this 
This is running at 7.8KHz, which kind of sucks (v 22KHz hearing, 44KHz sampling usually)

Credit for Cornell guys:
 Ken Colwell, Steve Fuertes
 ECE 476 Final Project
 April 2009

*/

#include <inttypes.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h> // for sine, exp
 
#define countTenMS 78 // ticks per 10mSec
#define FULL 255 // bottom of the hourglass; FULL == out of time
#define ALLSTRINGS 5 // NUMBER OF STRINGS ON STRINGPORT
#define G_MOD 32.0 // sharpness of Gaussian
 
// clear bit and set bit. You just need this. 
#define sbi(var, mask) ((var) |= (uint8_t)(1 << mask))
#define cbi(var, mask) ((var) &= (uint8_t)~(1 << mask)) 
 
// output controls
// note, b doesn't work on Arduino due to 6 and 7 being used by the crystal. so use D here
#define SIGNALPORT PORTD
#define SIGNALDIR DDRD
 
// input controls
#define STRINGPIN PINC
// actually this is only using the lowest 5. so 6 is free
#define STRINGDIR DDRC
// can define 'chord pin' to toggle chords. Left out of this demo.

// AD5330
// CS and WR used when setting vals. Note, I think you can get away w/out fiddling w/ them, but don't
#define CS 0 // = PB0 = digital 8 on Ard
#define WR 1 // = PB1 = digital 9 on Ard

//#define LDAC 16 - don't use pin. Tie low and forget it
//#define CLR 15 - don't use pin. Tie it High
//#define PD 8 - PD is enable. Just set it high!
//#define BUF 9 - don't use pin. tie BUF low - note, is HI in sample code.
//#define GAIN 14 set it low. means Gain = 1
 
//for a 32-bit DDS accumulator, running at 16e6/2048 (7812) Hz:
//increment = 549756*frequency

// what key is this?
const long incTable[14] = {228313667L, // G#
 241892640L, // A (440 Hz)
 271524488L, // B
 304784726L, // C#
 322871699L, // D
 362454131L, // E
 406819440L, // F#
 456627334L, // G#
 483785280L, // A (880 Hz)
 543048977L,  // B
 609514477L,  // C#
 645798373L,  // D
 724853286L,  // E
 0L};  // default, kills string
 
// The DDS variables
volatile unsigned long accumulator[ALLSTRINGS];
volatile unsigned char highByte[ALLSTRINGS];
volatile unsigned long increment[ALLSTRINGS];
volatile unsigned char hourglass[ALLSTRINGS];
 
/* tables for DDS */

unsigned char waveTable[256];
unsigned char rampTable[256] ; // envelope table: sharp decay, long release
unsigned long currentNote[5] ; // holds notes in the currently-selected chord
unsigned char currentInc[ALLSTRINGS] ; // each string has one of these;
// it describes which increment is attached to the string: (0,1,2,3)
// if the string is the oldest-played it gets 4 and doesn't play
unsigned char oldestInc, thisString;
 
volatile unsigned int time; // secondary timers driven off of "count"
volatile char count; // primary ISR timer
volatile int ii,jj; // index vars used in ISR and main() 
volatile char chordNum;   // state variables: which chord

// SDC - below is test sequence thing.
int testSeq = 0;
unsigned long lastChordTime;
char testPluck = 0;
int waveSeq = 0;

ISR (TIMER2_OVF_vect) //EVERY 128us:
{
 // run the accumulators through the table
   for(ii=0; ii<ALLSTRINGS; ii++)
   {
      accumulator[ii] += increment[ii] ;
      highByte[ii] = (char)(accumulator[ii] >> 24) ;
   }
 
 // output additive 8-bit signal to the DAC
 // use port based I/O. faster, and we need speed.
    cbi(PORTB, 0);    // CS 
    cbi(PORTB, 1); //WR
    SIGNALPORT = ((waveTable[highByte[0]]*rampTable[hourglass[0]])>>8)
    + ((waveTable[highByte[1]]*rampTable[hourglass[1]])>>8)
    + ((waveTable[highByte[2]]*rampTable[hourglass[2]])>>8)
    + ((waveTable[highByte[3]]*rampTable[hourglass[3]])>>8);
    sbi(PORTB, 1);  // WR   
    sbi(PORTB, 0); // CS

 // generate time base for MAIN
 // 78 counts is about 10 mSec
   count--;
   if (0 == count )
   {
      count=countTenMS;
      for (ii = 0; ii<ALLSTRINGS; ii++)
      if (hourglass[ii] < FULL) hourglass[ii]++; // "age" the strings
      time++;
   }
}

void loadSawWave() {
  cli();
    for (ii=0; ii<256; ii++)
    {  
       waveTable[ii] = ii/4;
    }   
  sei(); 
}

// note --- probably a better way to do this.
void loadSineWave() {
  cli();
    for (ii=0; ii<256; ii++)
    {
       waveTable[ii] = (char)(32.0 + (31.0 * sin(6.283*((float)ii)/256.0))) ;
    }   
   sei(); 
}

void loadSquareWave() {
  cli();
    for (ii=0; ii<256; ii++)
    { 
       if (ii < 128) {
           waveTable[ii] = 63;
       }
       else {
          waveTable[ii] = 0;
       }
    }   
   sei(); 
}

void loadTriWave() {
  cli();
    for (ii=0; ii<256; ii++)
    {
       if (ii < 128) {
          waveTable[ii] = ii/2;
       }
       else {
          waveTable[ii] = 128 - ii/2;
       }
    }   
   sei(); 
}

void loadGaussWave() {
  cli();
    for (ii=0; ii<256; ii++)
    {    
       //note that the Gaussian table below can be tuned "sharper" by decreasing defined G_MOD
      waveTable[ii] = (char)(63.0*exp(-1.0*(((((float)ii)-128.0)/G_MOD)*((((float)ii)-128.0)/G_MOD))));
    }   
   sei(); 
}

void setup()
{
    // set up output and input ports
    SIGNALDIR = 0xff ;
    STRINGDIR = 0x00 ;
    DDRB = 0xFF; // CS and WR
    pinMode(CS, OUTPUT);
    pinMode(WR, OUTPUT);
    // note, refer back to AD5330 datasheet/Sparkfun proj for details of 'opening sequence'
    sbi(PORTB, CS); //Set the CS high by default
    sbi(PORTB, WR);     //Set the WR pin high by default  

    // had - set clr high, ldac low    
    //Clock in Gain and Buffer Values
    cbi(PORTB, CS);
    delayMicroseconds(10);
    cbi(PORTB, WR);
    delayMicroseconds(10);
    
    cbi(PORTB, CS);
    delayMicroseconds(10);
    cbi(PORTB, WR);
    delayMicroseconds(10);

    // ALL tables range between 0-63 so we can add for 4x polyphony 
    // on an 8-bit DAC
    loadSineWave();

// note - is 'white noise' at end due to 'squeezing' the wave into a couple 
// possible values?

    for (ii=0; ii<10; ii++)  // Construct amplitude envelope
    {
        rampTable[ii] = (255-10*ii);
    } for (ii=10; ii<174; ii++) {
        rampTable[ii] = (174-ii);
    } for (ii=174; ii<256; ii++) {
        rampTable[ii] = 0;
    }
    
    // initialize strings
    for (ii=0; ii<ALLSTRINGS; ii++)
    {
        accumulator[ii] = 0L;
        hourglass[ii] = FULL;
        currentInc[ii] = ii;
    }
   
    // initialize timers
    count = countTenMS;
    time=0;
   
    // initialize to chord 0, A Major
    chordNum = 0;
    setChord(chordNum);
    
    for (ii=0; ii < ALLSTRINGS; ii++)
       increment[ii] = currentNote[ii];
    
    // timer 2 runs at 1/8 full rate 
    // one clock tick every
    // SDC notes: cornell code used timer 0, but arduino uses that for millis
    TCCR2B = 2 ; 
    //turn on timer 2 overflow ISR
    TIMSK2 = (1<<TOIE2) ;
 // zero for starts
    cbi(PORTB, CS);      
    cbi(PORTB, WR);
    SIGNALPORT = 0;
    sbi(PORTB, WR);       
    sbi(PORTB, CS);
  
    // turn on all ISRs
    sei();    
    
    // this for test only. Clear strings to start.
    testStrings(B0000000);
    lastChordTime = millis();
}
  
// this does things based on the plucking. in this case 'LOW' = 'plucked'
void pollStrings() {
       /**/ // POLL STRINGS
for (thisString=0; thisString<ALLSTRINGS; thisString++)
{
    if ( (~STRINGPIN) & (1<<thisString) ) //...then the string is being plucked
        {
            if (currentInc[thisString] < 4) //...then it's already attached to an increment
            {
                increment[currentInc[thisString]] = currentNote[thisString]; //reset freq
                hourglass[currentInc[thisString]] =0;  //play the note
            }
            else //...it isn't, so take the oldest one and give it to thisString
            {
                //find the oldest hourglass
                oldestInc=0;
                for (jj=1; jj < 4; jj++)
                {
                   if (hourglass[jj] > hourglass[oldestInc])
                   oldestInc = jj;
                }
           
                //set that string's inc to 4
                for (jj=0; jj < ALLSTRINGS; jj++)
                {
                   if (currentInc[jj] == oldestInc)
                       currentInc[jj] = 4;
                }
                //set the new string's inc to oldestInc and play the note
                
                currentInc[thisString] = oldestInc;
                increment[oldestInc] = currentNote[thisString];
                hourglass[oldestInc] = 0;
            } // else
        } // plucked
    } // poll loop  
}
 
// test strings - just pass in a 'dummy' 8 bit thing. 
// note: on the other LOW is plucked. but here HIGH is plucked.
void testStrings(char plucked) {

  for (thisString=0; thisString<ALLSTRINGS; thisString++)
  {
    if ( (plucked) & (1<<thisString) ) //...then the string is being plucked
        {
            if (currentInc[thisString] < 4) //...then it's already attached to an increment
            {
                increment[currentInc[thisString]] = currentNote[thisString]; //reset freq
                hourglass[currentInc[thisString]] =0;  //play the note
            }
            else //...it isn't, so take the oldest one and give it to thisString
            {
                //find the oldest hourglass
                oldestInc=0;
                for (jj=1; jj < 4; jj++)
                {
                   if (hourglass[jj] > hourglass[oldestInc])
                   oldestInc = jj;
                }
           
                //set that string's inc to 4
                for (jj=0; jj < ALLSTRINGS; jj++)
                {
                   if (currentInc[jj] == oldestInc)
                       currentInc[jj] = 4;
                }
                //set the new string's inc to oldestInc and play the note
                
                currentInc[thisString] = oldestInc;
                increment[oldestInc] = currentNote[thisString];
                hourglass[oldestInc] = 0;
            } // else
        } // plucked
    } // poll loop  
} 

void setChord(int chordNum) {  
     // CHANGE CHORD
    switch (chordNum)
    {
    case 0: // A MAJOR
        currentNote[0] = incTable[1];
        currentNote[1] = incTable[3];
        currentNote[2] = incTable[5];
        currentNote[3] = incTable[8];
        currentNote[4] = incTable[10];
    break;
    case 1: // B MINOR
        currentNote[0] = incTable[2];
        currentNote[1] = incTable[4];
        currentNote[2] = incTable[6];
        currentNote[3] = incTable[9];
        currentNote[4] = incTable[11];
    break;
    case 2: // C# MINOR
        currentNote[0] = incTable[0];
        currentNote[1] = incTable[3];
        currentNote[2] = incTable[5];
        currentNote[3] = incTable[7];
        currentNote[4] = incTable[10];
    break;
    case 3: // D MAJOR
        currentNote[0] = incTable[1];
        currentNote[1] = incTable[4];
        currentNote[2] = incTable[6];
        currentNote[3] = incTable[8];
        currentNote[4] = incTable[11];
    break;
    case 4: // E MAJOR
        currentNote[0] = incTable[2];
        currentNote[1] = incTable[5];
        currentNote[2] = incTable[7];
        currentNote[3] = incTable[9];
        currentNote[4] = incTable[12];
    break;
    case 5: // F# MINOR
        currentNote[0] = incTable[1];
        currentNote[1] = incTable[3];
        currentNote[2] = incTable[6];
        currentNote[3] = incTable[8];
        currentNote[4] = incTable[10];
    break;
    default:
    break;
    }   
}
 
// to do - first just bang out some chords instead of polling.
// then hook up the string plucking business
// also cycle over waves
void loop()
{
    
    if (millis() - lastChordTime > 200) {
        testPluck = 0;
        sbi(testPluck, testSeq); 
        testStrings(testPluck);  
        testSeq = (testSeq + 1) % ALLSTRINGS;

        if (testSeq == 0) {
          
          waveSeq = (waveSeq + 1) % 5;
          // note, you pretty much have to temporarily
          // suspend interrupts whilst loading these.
          // gauss seems most fun (string like)
          // saw is harshest (no surprise)
          // sine is 'sweet' like a bell
          // square is vid game like
          // tri is like a bell
          delay(4000);
          switch (waveSeq) {
          case 0:
            loadSineWave();
            break;
          case 1:
            loadSquareWave();
            break;
          case 2:
            loadGaussWave();
            break;
          case 3:
            loadTriWave();
            break;
          case 4:
            loadSawWave();
          }
        }
        lastChordTime = millis();
    }
        
    if (time==5) //...then 50ms have elapsed
    {
        time=0; //reset timer
        // ordinarily would:
        // POLL STRINGS
        // POLL CHORD BUTTONS (logic LO is button PRESSED)             
    } // end 50ms timer
} // end loop()
