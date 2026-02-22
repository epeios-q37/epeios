import ucuq

ring = None
buzzer = None
oled = None
lcd = None

def connect(device):
  global ring, buzzer, oled, lcd
  ucuq.setDevice(device)
  
  ring = ucuq.Ravel.Ring()
  buzzer = ucuq.Ravel.Buzzer()
  oled = ucuq.Ravel.OLED()
  lcd = ucuq.Ravel.LCD()
  
  
def launch():
  lcd.moveTo(0,0).putString("Donnons un futur").moveTo(0,1).putString("  a nos ados !").backlightOn()