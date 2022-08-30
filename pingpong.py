from machine import Pin,SPI,PWM
import framebuf
import time
import _thread

#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

ball_pos = [50, 75]
ball_angles = [1, 1]

sq_size = 10
col = WHITE

bl_sizes = (20, 2)
bl_col = WHITE

p1_pos = 30
p2_pos = 30
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

def ball(lcd, pos):
    
    y, x = pos
    lcd.line(x, y, x + sq_size, y, col)
    lcd.line(x + sq_size, y, x + sq_size, y + sq_size, col)
    lcd.line(x + sq_size, y + sq_size, x, y + sq_size, col)
    lcd.line(x, y + sq_size, x, y, col)

def block(lcd, pos):
    y, x = pos
    lcd.line(x, y, x + bl_sizes[1], y, bl_col)
    lcd.line(x + bl_sizes[1], y, x + bl_sizes[1], y + bl_sizes[0], bl_col)
    lcd.line(x + bl_sizes[1], y + bl_sizes[0], x, y + bl_sizes[0], bl_col)
    lcd.line(x, y + bl_sizes[0], x, y, bl_col)

def update_ball_pos():
    
    if 3 <= ball_pos[1] and ball_pos[1] <= 5:
        if (p1_pos + bl_sizes[0] >= ball_pos[0] and ball_pos[0] >= p1_pos) or (p1_pos + bl_sizes[0] >= ball_pos[0] + sq_size and ball_pos[0] + sq_size >= p1_pos):
            ball_angles[0] *= -1
    
    if ball_pos[1] + sq_size >= 152 and 154 >= ball_pos[1] + sq_size:
        if (p2_pos + bl_sizes[0] >= ball_pos[0] and ball_pos[0] >= p1_pos) or (p2_pos + bl_sizes[0] >= ball_pos[0] + sq_size and ball_pos[0] + sq_size >= p1_pos):
            ball_angles[0] *= -1
    
    ball_pos[0] += ball_angles[1]
    ball_pos[1] += ball_angles[0]
    
    
    if ball_pos[1] > 158 - sq_size:
        print("Player Left wins!")
        while True:
            continue
    elif ball_pos[1] < 0:
        print("Player Right wins!")
        while True:
            continue
    
    if ball_pos[0] > 78 - sq_size or ball_pos[0] < 0:
        ball_angles[1] *= -1
    
    return ball_pos

def display_game(lcd):

    #tall things
    lcd.fill(BLACK)
    block(lcd, (p1_pos, 5))
    block(lcd, (p2_pos, 152))
    ball(lcd, ball_pos)
    
    lcd.display()

if __name__=='__main__':
    lcd = LCD_0inch96()
    while True:
        display_game(lcd)
        update_ball_pos()
