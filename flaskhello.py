from flask import Flask
import RPi.GPIO as GPIO
import time
import smbus #for lcd
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

###  lcd setup ###
# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  # mode = 0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits): # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line): # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
  
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

###  buzzer setup  ###
buzzer = 5
GPIO.setup(buzzer,GPIO.IN)
GPIO.setup(buzzer,GPIO.OUT)
print("buzzer ready")

def buzz(pitch, duration):   #create the function “buzz” and feed it the pitch and duration)
 
  if(pitch==0):
   time.sleep(duration)
   return
  period = 1.0 / pitch   #period is the inverse of frequency
  delay = period / 2     #calcuate the time for half of the wave  
  cycles = int(duration * pitch)   #the number of waves to produce is the duration times the frequency

  for i in range(cycles):    #start a loop from 0 to the variable “cycles” calculated above
   GPIO.output(buzzer, True)   #set buzzer to HIGH
   time.sleep(delay)    #wait
   GPIO.output(buzzer, False)  #set buzzer to LOW
   time.sleep(delay)    #wait

def play(tune):
  x=0 #initial index in duration list(if there is any)
  if(tune==1): #doorbell tune
    pitches=[262,294,330,349,392,440,494,523, 587, 659,698,784,880,988,1047]
    duration=0.1
    for p in pitches:
      buzz(p, duration)  #feed the pitch and duration to the function, “buzz”
      time.sleep(duration *0.5)
    for p in reversed(pitches):
      buzz(p, duration)
      time.sleep(duration *0.5)

  elif(tune==2): #welcome tune
    pitches=[262,330,392,523,1047]
    duration=[0.2,0.2,0.2,0.2,0.2,0,5]
    for p in pitches:
      buzz(p, duration[x])  
      time.sleep(duration[x] *0.5)
      x+=1
  elif(tune==3): #access denied tune
    pitches=[392,294,0,392,294,0,392,0,392,392,392,0,1047,262]
    duration=[0.2,0.2,0.2,0.2,0.2,0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.8,0.4]
    for p in pitches:
      buzz(p, duration[x])  
      time.sleep(duration[x] *0.5)
      x+=1

  elif(tune==4):
    pitches=[1047, 988,659]
    duration=[0.1,0.1,0.2]
    for p in pitches:
      buzz(p, duration[x])  
      time.sleep(duration[x] *0.5)
      x+=1

  elif(tune==5):
    pitches=[1047, 988,523]
    duration=[0.1,0.1,0.2]
    for p in pitches:
      buzz(p, duration[x])  
      time.sleep(duration[x] *0.5)
      x+=1

GPIO.setup(22,GPIO.OUT) #set up servo(act as doorlock)
p = GPIO.PWM(22,50) #pwm at 50Hz
lcd_init()
app = Flask(__name__)

@app.route('/') #home page path
def myhtml(): #home page html file
    return """
<html>
    <head>
        <title>Smart Receptionist with Smartlock System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <link rel="stylesheet" href="style.css">
        <link href="https://fonts.googleapis.com/css?family=Source+Code+Pro:600|Teko:500" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css?family=Orbitron:400,700" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-sm bg-dark navbar-dark d-flex justify-content-between">
          <div class="p-2"><a class="navbar-brand" href="#">Smart Receptionist with Smartlock System </a></div> 
        </nav>
        <div class="container">
            <div class="row">
                <div class="col">
                    <button type="button" class="btn btn-block btn-info" id="turnOnBtn"><a href="/turnon">Unlock</button>
                </div>
                <div class="col">
                    <button type="button" class="btn btn-block btn-danger" id="turnOffBtn"><a href="/turnoff">Keep Locked</button>
                </div>
            </div>
        </div>
    </body>
</html>"""

@app.route('/turnon') #turn on servo path
def turnon():
    p.start(7.5) #set servo to the right position(locked)

    p.ChangeDutyCycle(7.5) #locked dutycycle=1.5ms/20ms=7.5%
    time.sleep(2)
    p.ChangeDutyCycle(2.5) #opened dutycycle=0.5ms/20ms=2.5%
    time.sleep(2)
    p.ChangeDutyCycle(7.5) #locked
    time.sleep(1)
    
    #welcome vistor
    lcd_string("",LCD_LINE_1)
    lcd_string("   Welcome!!!",LCD_LINE_2)
    lcd_string("",LCD_LINE_3)
    lcd_string("",LCD_LINE_4)
    play(3) #play welcome tune
    
    GPIO.setup(19,GPIO.OUT) #green
    for num in range(5): #green   
        GPIO.output(19,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(19,GPIO.LOW)
        time.sleep(0.5)
    time.sleep(3)
    
    GPIO.cleanup()
    return "Successfully Unlocked!"

@app.route('/turnoff') #turn off servo path
def turnoff():
    #visitor is rejected
    lcd_string("Access Denied",LCD_LINE_2)
    
    play(2)
    
    GPIO.setup(17,GPIO.OUT) #red
    for num in range(5): #red
        GPIO.output(17,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(17,GPIO.LOW)
        time.sleep(0.5)
    time.sleep(3)
    
    return "Successfully Keep Locked!"

# Launch the Flask dev server
app.run(host="0.0.0.0", debug=True)
#host is 0.0.0.0 to make it global
#host will be 0.0.0.0:5000 by defaut and you have to change 0.0.0.0 to your RPi's IP address
