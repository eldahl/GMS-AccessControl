#define relay 4     // Set Relay Pin

void setup() {
  //Arduino Pin Configuration
  pinMode(A2,INPUT_PULLUP);
  pinMode(A4,OUTPUT);
  pinMode(A3,OUTPUT);
  pinMode(relay, OUTPUT);

  //Be careful how relay circuit behave on while resetting or power-cycling your Arduino
  digitalWrite(relay, HIGH); // Make sure door is locked
  
  Serial.begin(9600);  // Initialize serial communications with PC
  Serial.println(F("Access Control Example v0.1"));
}

void loop () {
  if (Serial.read() == 'o')
    AABEN_LUK();
}

int a=1;
int b=0;
void AABEN_LUK() {
  unsigned long tid = millis();
  digitalWrite(A4,a);
  digitalWrite(A3,b);
  delay(300);
  
  while ((analogRead(A5)<300)  &&  ((tid + 3500) > millis() ) ) {  Serial.println(analogRead(A5));};
  digitalWrite(A4,b);
  digitalWrite(A3,a);
  
  tid = millis();
  
  while(digitalRead(A2) == 0  && ((tid + 3500) > millis() ) ){} // venter på kontakt i stillingt neutral
  digitalWrite(A4,0);
  digitalWrite(A3,0);
  
  // Change lock spin direction for next function call
  if (a==1) {
    a=0;
    b=1;
  }
  else {
    a=1;
    b=0;
  }
}