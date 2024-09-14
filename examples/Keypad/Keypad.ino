// (·) F 8
// (·) E 9
// (·) D 2
// (·) B 4
// (·) C 3
// (·) A 5
// (·) G 7
// (·) H 6

#include <Keypad.h>

// Define the number of rows and columns in the keypad
const byte ROWS = 4;
const byte COLS = 4;

// Define the keys in the keypad
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

// Connect the keypad ROW pins to these Arduino pins
// E F G H
byte rowPins[ROWS] = {9, 8, 7, 6};

// Connect the keypad COLUMN pins to these Arduino pins
// A B C D
byte colPins[COLS] = {5, 4, 3, 2};

// Create the Keypad object
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
  // Start the serial communication
  Serial.begin(9600);
}

void loop() {
  // Get the key pressed
  char key = keypad.getKey();

  // If a key is pressed
  if (key) {
    // Log the key to the serial monitor
    Serial.print("Key Pressed: ");
    Serial.println(key);
  }
}
