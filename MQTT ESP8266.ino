#include <Bounce2.h> // Used for "debouncing" the pushbutton
#include <ESP8266WiFi.h> // Enables the ESP8266 to connect to the local network (via WiFi)
#include <PubSubClient.h> // Allows us to connect to, and publish to the MQTT broker

#define NUM_BUTTONS 4 //Number of buttons
const uint8_t BUTTON_PINS[NUM_BUTTONS] = {5, 4, 14, 12}; //Button Pins
const uint8_t LED_PINS[NUM_BUTTONS-1] = {13, 15, 16}; //Led Pints

Bounce * buttons = new Bounce[NUM_BUTTONS];

//Wifi Settings
const char* ssid = "TelstraE7C483";
const char* wifi_password = "hc32tkcc6e";

//MQTT Settings
const char* mqtt_server = "192.168.0.131"; //RPI IP
const char* mqtt_topic = "button"; //topic
const char* mqtt_username = "raspberrypi";
const char* mqtt_password = "password";
const char* clientID = "ESP8266";



  
// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, wifiClient); // 1883 is the listener port for the Broker

void setup() {
  //Initialise buttons
  for (int i = 0 ; i < NUM_BUTTONS ; i++)
  {
    buttons[i].attach( BUTTON_PINS[i] , INPUT); 
    buttons[i].interval(5); 
  }
  //intiialise leds
  for (int i = 0 ; i < NUM_BUTTONS - 1; i++)
  {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  
  // Begin Serial on 115200
  Serial.begin(115200);

  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Debugging - Output the IP Address of the ESP8266
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Connect to MQTT Broker
  if (client.connect(clientID, mqtt_username, mqtt_password)) {
    Serial.println("Connected to MQTT Broker!");
  }
  else {
    Serial.println("Connection to MQTT Broker failed...");
  }
}

//Sends a message to the server
void SendMessage(char* i)
{
  if (client.publish(mqtt_topic, i))
  {
    Serial.println("Button pushed and message sent!");
  }
  else
  {
    Serial.println("Message failed to send. Reconnecting to MQTT Broker and trying again");
    client.connect(clientID, mqtt_username, mqtt_password);
    delay(20); // This delay ensures that client.publish doesn't clash with the client.connect call
    client.publish(mqtt_topic, i);
  } 
}

//turns off the leds
void TurnOffLeds()
{
  for (int i = 0; i < NUM_BUTTONS; i++)  
  {
    digitalWrite(LED_PINS[i], LOW);
  }
}


void loop() {
  //loops through the buttons  
  for (int i = 0; i < NUM_BUTTONS; i++)  
  {
    //updates the button states
    buttons[i].update();

    //if button pressed
    if ( buttons[i].fell() ) 
    {
      switch (i)
      {
        case 0:
        //turn on/off corrosponding LED
         if (digitalRead(LED_PINS[i]) == HIGH){
            TurnOffLeds();
         }
         else {
          TurnOffLeds();
          digitalWrite(LED_PINS[i], HIGH);
         }
         //send message with button #
         Serial.println('0');
          SendMessage("0");
          break;
         case 1:
         if (digitalRead(LED_PINS[i]) == HIGH){
            TurnOffLeds();
         }
         else {
          TurnOffLeds();
          digitalWrite(LED_PINS[i], HIGH);
         }
         Serial.println('1');
         SendMessage("1");
          break;
         case 2:
         if (digitalRead(LED_PINS[i]) == HIGH){
            TurnOffLeds();
         }
          else {
          TurnOffLeds();
          digitalWrite(LED_PINS[i], HIGH);
          }
          Serial.println('2');
          SendMessage("2");
          break;
         case 3:
          Serial.println('3');
          SendMessage("3");
          TurnOffLeds();
          break;
      }
    }    
  }
}