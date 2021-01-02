import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import smbus #for lcd
from flask import Flask
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

### ultrasonic sensor setup ###
GPIO_TRIGGER = 18
GPIO_ECHO = 20
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    GPIO.output(GPIO_TRIGGER, True) # set Trigger to HIGH
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False) # set Trigger to LOW after 0.01ms
 
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time() # save StartTime
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time() # save time of arrival
    
    TimeElapsed = StopTime - StartTime
    # time difference between start and arrival
    distance = (TimeElapsed * 34300) / 2
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because goes there and back
    return distance

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
  if(tune==1): 
    pitches=[262,294,330,349,392,440,494,523, 587, 659,698,784,880,988,1047]
    duration=0.1
    for p in pitches:
      buzz(p, duration)  #feed the pitch and duration to the function, “buzz”
      time.sleep(duration *0.5)
    for p in reversed(pitches):
      buzz(p, duration)
      time.sleep(duration *0.5)

  elif(tune==2): #access denied tune
    pitches=[262,330,392,523,1047]
    duration=[0.2,0.2,0.2,0.2,0.2,0,5]
    for p in pitches:
      buzz(p, duration[x])  
      time.sleep(duration[x] *0.5)
      x+=1
  elif(tune==3): #welcome tune
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

  elif(tune==5): #doorbell tune
    pitches=[1047, 988,523]
    duration=[0.1,0.1,0.2]
    for p in pitches:
      buzz(p, duration[x])  
      time.sleep(duration[x] *0.5)
      x+=1

def send_email(): #define send email function
    import smtplib
    #import library for sending an image with email
    from email.mime.multipart import MIMEMultipart  
    from email.mime.base import MIMEBase  
    from email.mime.text import MIMEText  
    from email.utils import formatdate  
    from email import encoders

    ADDRESS = ''  #sender's email address
    PASSWORD = ''  #sender's email password
    subject = 'Smart Receptionist with Smartlock System'             
  
    msg = MIMEMultipart()  
    msg['Subject'] = subject  
    msg['From'] = ADDRESS 
    msg['To'] = ADDRESS
    #the link is whereyou can control servo
    body = 'You have a vistor at your door right now, please go to this link: http://:5000/' 
    msg.attach(MIMEText(body,'plain'))  
  
    image = 'pic.jpg'
    attachment = open(image, 'rb')

    part = MIMEBase('application', "octet-stream")  
    part.set_payload((attachment).read())  
    encoders.encode_base64(part)  
    part.add_header('Content-Disposition', 'attachment; filename="pic.jpg"')   # File name and format name
    msg.attach(part)  
  

    s = smtplib.SMTP('smtp.gmail.com', 587)  #set up smtp
    s.ehlo()  
    s.starttls()  
    s.ehlo()  
    s.login(ADDRESS, PASSWORD) #log in the email  
    s.sendmail(ADDRESS,ADDRESS, msg.as_string()) #smtp.sendmail(sender,receiver,message) 
    s.quit()  
    
    
#####           Let's Start!!!           #####


#enable pull down resistor, set input to LOW
GPIO.setup(21,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    #when button is pressed, pin 21 connects to 5V, state becomes HIGH
    #visitor presses door button
    if GPIO.input(21) == True:
        break

print("button pressed")
time.sleep(0.2) #avoid bouncing
play(5) #play doorbell tune
            
camera = PiCamera()
lcd_init()  #initialise lcd
        
#tell visitor to face the camera
lcd_string("Please face the",LCD_LINE_2)
lcd_string("Camera",LCD_LINE_3)
time.sleep(3)
        
camera.start_preview() #start preview
time.sleep(4)

pic_captured = False
#when picture is not captured due to distance
while pic_captured == False:
    dist = distance() #ultrasonic sensor detects distance
    print ("Measured Distance = %.1f cm" % dist)
    if dist >= 20 and dist <= 50:
        #automatically captures picture when distance is good
        camera.capture('pic.jpg') #assigns name to captured picture
        #picture is captured, jump out of the loop
        pic_captured = True
    else:
        #notify visitor to keep the right distance
        lcd_string("Please keep 30cm away",LCD_LINE_2)
        lcd_string("From the camera",LCD_LINE_3)
    time.sleep(1)

camera.stop_preview() #stop preview
#send_email() #send an email
print("send an email")

#notify visitor the progress
lcd_string("Image is taken",LCD_LINE_1)
lcd_string("",LCD_LINE_2)
lcd_string("Sending image",LCD_LINE_3)
lcd_string("To server...",LCD_LINE_4)
time.sleep(3)
        