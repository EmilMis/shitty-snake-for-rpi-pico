from machine import Pin,SPI,PWM
import framebuf
import time
import _thread
import random

#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

KEY_UP = Pin(2,Pin.IN,Pin.PULL_UP)
KEY_DOWN = Pin(18,Pin.IN,Pin.PULL_UP)
KEY_LEFT= Pin(16,Pin.IN,Pin.PULL_UP)
KEY_RIGHT= Pin(20,Pin.IN,Pin.PULL_UP)
KEY_CTRL=Pin(3,Pin.IN,Pin.PULL_UP)
KEY_A=Pin(15,Pin.IN,Pin.PULL_UP)
KEY_B=Pin(17,Pin.IN,Pin.PULL_UP)

last_dir = 3
snake_pos = [[0, 0], [0, 1]]
apple_pos = [0, 0]

class LCD_0inch96(framebuf.FrameBuffer):
    def __init__(self):
    
        self.width = 160
        self.height = 80
        
        self.cs = Pin(9,Pin.OUT)
        self.rst = Pin(12,Pin.OUT)
#        self.bl = Pin(13,Pin.OUT)
        self.cs(1)
        # pwm = PWM(Pin(13))#BL
        # pwm.freq(1000)        
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(10),mosi=Pin(11),miso=None)
        self.dc = Pin(8,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.Init()
        self.SetWindows(0, 0, self.width-1, self.height-1)
        
    def reset(self):
        self.rst(1)
        time.sleep(0.2) 
        self.rst(0)
        time.sleep(0.2)         
        self.rst(1)
        time.sleep(0.2) 
        
    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))

    def write_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def backlight(self,value):#value:  min:0  max:1000
        pwm = PWM(Pin(13))#BL
        pwm.freq(1000)
        if value>=1000:
            value=1000
        data=int (value*65536/1000)       
        pwm.duty_u16(data)  
        
    def Init(self):
        self.reset() 
        self.backlight(10000)  
        
        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x21) 
        self.write_cmd(0x21) 

        self.write_cmd(0xB1) 
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB2)
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB3) 
        self.write_data(0x05)  
        self.write_data(0x3A)
        self.write_data(0x3A)
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB4)
        self.write_data(0x03)

        self.write_cmd(0xC0)
        self.write_data(0x62)
        self.write_data(0x02)
        self.write_data(0x04)

        self.write_cmd(0xC1)
        self.write_data(0xC0)

        self.write_cmd(0xC2)
        self.write_data(0x0D)
        self.write_data(0x00)

        self.write_cmd(0xC3)
        self.write_data(0x8D)
        self.write_data(0x6A)   

        self.write_cmd(0xC4)
        self.write_data(0x8D) 
        self.write_data(0xEE) 

        self.write_cmd(0xC5)
        self.write_data(0x0E)    

        self.write_cmd(0xE0)
        self.write_data(0x10)
        self.write_data(0x0E)
        self.write_data(0x02)
        self.write_data(0x03)
        self.write_data(0x0E)
        self.write_data(0x07)
        self.write_data(0x02)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x12)
        self.write_data(0x27)
        self.write_data(0x37)
        self.write_data(0x00)
        self.write_data(0x0D)
        self.write_data(0x0E)
        self.write_data(0x10)

        self.write_cmd(0xE1)
        self.write_data(0x10)
        self.write_data(0x0E)
        self.write_data(0x03)
        self.write_data(0x03)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x02)
        self.write_data(0x08)
        self.write_data(0x0A)
        self.write_data(0x13)
        self.write_data(0x26)
        self.write_data(0x36)
        self.write_data(0x00)
        self.write_data(0x0D)
        self.write_data(0x0E)
        self.write_data(0x10)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0x36)
        self.write_data(0xA8)

        self.write_cmd(0x29) 
        
    def SetWindows(self, Xstart, Ystart, Xend, Yend):#example max:0,0,159,79
        Xstart=Xstart+1
        Xend=Xend+1
        Ystart=Ystart+26
        Yend=Yend+26
        self.write_cmd(0x2A)
        self.write_data(0x00)              
        self.write_data(Xstart)      
        self.write_data(0x00)              
        self.write_data(Xend) 

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(Ystart)
        self.write_data(0x00)
        self.write_data(Yend)

        self.write_cmd(0x2C) 
        
    def display(self):
    
        self.SetWindows(0,0,self.width-1,self.height-1)       
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)        
            

def random_apple_pos():
    free_poss = []
    for i in range(8):
        for j in range(16):
            free_poss.append([i, j])
    for body in snake_pos:
        free_poss.remove(body)
    return random.choice(free_poss)

def fill_square(p1, p2, lcd, col):
    for i in range(p1[0], p2[0]):
        lcd.line(p1[1], i, p2[1], i, col)

def game_over(lcd):
    for i in range(100, 60, -1):
        lcd.backlight(i)
        time.sleep(0.03)
    lcd.text("GAME OVER", 35, 15, RED)
    lcd.display()
    while True:
        continue

def display_game(lcd, snake_pos, apple_pos):
    head = snake_pos[-1]
    if head[0] < 0 or head[0] >= 8 or head[1] < 0 or head[1] >= 16:
        game_over(lcd)
    for body in snake_pos[:-1]:
        if body == head:
            game_over(lcd)
    lcd.fill(WHITE)
    i=0
    while(i<=80):    
        lcd.hline(0,i,160,BLACK)
        i=i+10  
    i=0
    while(i<=160):
        lcd.vline(i,0,80,BLACK)
        i=i+10
    fill_square((apple_pos[0] * 10, apple_pos[1] * 10), ((apple_pos[0] + 1) * 10, (apple_pos[1] + 1) * 10), lcd, RED)
    for (x, y) in snake_pos:
        x *= 10
        y *= 10
        fill_square((x, y), (x + 10, y + 10), lcd, GREEN)
    lcd.display()

def update_snake(snake_pos, last_dir):
    if last_dir == 1:
        snake_pos.append([snake_pos[-1][0] - 1, snake_pos[-1][1]])
    elif last_dir == 2:
        snake_pos.append([snake_pos[-1][0] + 1, snake_pos[-1][1]])
    elif last_dir == 3:
        snake_pos.append([snake_pos[-1][0], snake_pos[-1][1] + 1])
    elif last_dir == 4:
        snake_pos.append([snake_pos[-1][0], snake_pos[-1][1] - 1])

if __name__=='__main__':
    lcd = LCD_0inch96()
    lcd.backlight(70)
    apple_pos = random_apple_pos()
    apple_pos = [0, 10]
    while True:
        update_snake(snake_pos, last_dir)
        if snake_pos[-1] != apple_pos:
            snake_pos.pop(0)
        else:
            apple_pos = random_apple_pos()
        display_game(lcd, snake_pos, apple_pos)
            
        for i in range(8000):
            if not KEY_UP.value():
                last_dir = 1
            elif not KEY_DOWN.value():
                last_dir = 2
            elif not KEY_RIGHT.value():
                last_dir = 3
            elif not KEY_LEFT.value():
                last_dir = 4
        

