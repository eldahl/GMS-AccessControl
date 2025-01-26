#include <Adafruit_NeoPixel.h>
#include "WS2812_Definitions.h"

// Motor control
// Channel A
int directionPin = 12;
int pwmPin = 3;
int brakePin = 9;
int CHAN_A_CUR_SENSE = A0;
//uncomment if using channel B, and remove above definitions
//int directionPin = 13;
//int pwmPin = 11;
//int brakePin = 8;
#define NeutralPinIn 4
#define NeutralPinOut 2
float currentSense = 0;

// LED Indicator
#define PIN 5
#define LED_COUNT 8
// Library for WS2812 by Adafruit
Adafruit_NeoPixel leds = Adafruit_NeoPixel(LED_COUNT, PIN, NEO_GRB + NEO_KHZ800);

//boolean to switch direction
bool lockState = false;

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Starts in unlocked state, in neutral position
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
void setup() {
  Serial.begin(9600);

  // LEDS
  leds.begin();
  leds.setBrightness(100);
  clearLEDs();
  leds.show();

	// Motor control
	pinMode(directionPin, OUTPUT);
	pinMode(pwmPin, OUTPUT);
	pinMode(brakePin, OUTPUT);

  pinMode(NeutralPinIn, INPUT_PULLUP);
  pinMode(NeutralPinOut, OUTPUT);
  digitalWrite(NeutralPinOut, LOW);
  GoToNeutral();
  lockState == true ? setAllColor(255, 0, 0) : setAllColor(0, 255, 0);
}

void loop() {

  char serialIn = Serial.read();
  if(serialIn == 'o') {
    // Toggle lock
    ToggleLock();
    // Set LED Indicator color
    lockState == true ? setAllColor(255, 0, 0) : setAllColor(0, 255, 0);
  }
  else if(serialIn == 'i') {
    // Report state
    Serial.println("The lock state is: " + lockState ? "Locked" : "Open");
  }
  else if(serialIn == 'k') {
    GoToNeutral();
  }
}

void ToggleLock(){
  digitalWrite(directionPin, lockState == true ? HIGH : LOW);

  //release breaks
  digitalWrite(brakePin, LOW);

  //set work duty for the motor
  analogWrite(pwmPin, 250);

  delay(250);
  // Measure motor load
  while(MeasureMotorLoad());

  //activate breaks
  digitalWrite(brakePin, HIGH);

  //set work duty for the motor to 0 (off)
  analogWrite(pwmPin, 0);
  
  lockState = !lockState;
  GoToNeutral();
}

bool MeasureMotorLoad() {
  //currentSense = 0.05 * analogRead(CHAN_A_CUR_SENSE) + 0.95 * currentSense;
  float sum = 0;
  for(int i = 0; i < 25; i++) {
    sum += analogRead(CHAN_A_CUR_SENSE);
  }
  currentSense = sum / 25;
  Serial.println(currentSense);
  return currentSense < 50;
}

void GoToNeutral() {
  digitalWrite(directionPin, lockState == true ? HIGH : LOW);

  //release breaks
  digitalWrite(brakePin, LOW);

  //set work duty for the motor
  analogWrite(pwmPin, 250);
  
  delay(250);
  while(MeasureNeutralSwitch() != HIGH && MeasureMotorLoad());
  
  //activate breaks
  digitalWrite(brakePin, HIGH);

  //set work duty for the motor to 0 (off)
  analogWrite(pwmPin, 0);
}

int MeasureNeutralSwitch() {
  return digitalRead(NeutralPinIn);
}

void clearLEDs() {
  for (int i=0; i<LED_COUNT; i++) {
      leds.setPixelColor(i, 0);
  }
}

void setAllColor(byte r, byte g, byte b) {
  for (int i = 0; i < LED_COUNT; i++) {
      leds.setPixelColor(i, r,g,b);
  }
  leds.show();
}