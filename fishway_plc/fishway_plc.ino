const int LED_UP_PIN = 8;    // LED for up command
const int LED_DOWN_PIN = 9;   // LED for down command

// Status pin number
const uint8_t STATUS_UP = 2;
const uint8_t STATUS_DOWN = 3;
const uint8_t STATUS_PRESSURE = 4;
const uint8_t STATUS_OIL = 5;
const uint8_t STATUS_MOTOR = 6;

// For debouncing
unsigned long lastChangeTime = 0;
const unsigned long debounceDelay = 50; // 50ms

String receivedCommand = "";
bool commandComplete = false;

// Each bit represents each status
uint8_t previousStatus = 0;
uint8_t currentStatus = 0;

void setup() {
  // Initialize Serial1 communication
  Serial1.begin(9600);
  Serial.begin(9600);
  
  // Initialize LED pins
  pinMode(LED_UP_PIN, OUTPUT);
  pinMode(LED_DOWN_PIN, OUTPUT);
  pinMode(STATUS_UP, INPUT_PULLUP);
  pinMode(STATUS_DOWN, INPUT_PULLUP);
  pinMode(STATUS_PRESSURE, INPUT_PULLUP);
  pinMode(STATUS_OIL, INPUT_PULLUP);
  pinMode(STATUS_MOTOR, INPUT_PULLUP);
  
  // Turn off all LEDs initially
  digitalWrite(LED_UP_PIN, LOW);
  digitalWrite(LED_DOWN_PIN, LOW);

  Serial1.println("Arduino ready - waiting for commands");
}

void loop() {
  // Read incoming Serial1 data
  while (Serial1.available()) {
    char inChar = (char)Serial1.read();
    
    if (inChar == '\n') {
      commandComplete = true;
    } else {
      receivedCommand += inChar;
    }
  }
  
  // Process complete command
  if (commandComplete) {
    receivedCommand.trim(); // Remove any whitespace
    
    Serial1.print("Received: ");
    Serial1.println(receivedCommand);
    
    if (receivedCommand == "up") {
      digitalWrite(LED_UP_PIN, HIGH);
      digitalWrite(LED_DOWN_PIN, LOW);
      Serial1.println("LED UP ON");
    }
    else if (receivedCommand == "down") {
      digitalWrite(LED_DOWN_PIN, HIGH);
      digitalWrite(LED_UP_PIN, LOW);
      Serial1.println("LED DOWN ON");
    }
    else if (receivedCommand == "stop") {
      digitalWrite(LED_UP_PIN, LOW);
      digitalWrite(LED_DOWN_PIN, LOW);
      Serial1.println("ALL LEDs OFF");
    }
    else {
      Serial1.println("Unknown command");
    }
    
    // Reset for next command
    receivedCommand = "";
    commandComplete = false;
  }
  previousStatus = currentStatus;
  for(int i = STATUS_UP; i < STATUS_MOTOR + 1; i++){
    currentStatus = currentStatus << 1;
    currentStatus += digitalRead(i);
  }
  currentStatus = currentStatus & 0b00011111;

  if(currentStatus != previousStatus){
    unsigned long now = millis();
    if(now - lastChangeTime > debounceDelay){
      Serial.print(previousStatus, BIN);
      Serial.print(", ");
      Serial.println(currentStatus, BIN);
      Serial1.println(currentStatus);
      lastChangeTime = now;
    }
  }
}