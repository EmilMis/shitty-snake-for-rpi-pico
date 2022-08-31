from machine import Pin,SPI,PWM
import framebuf
import time
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

you_cannot = ["you cant put that here", "YOU. CANNOT. DO. THAT.", "...", ".....", "please stop", "why do you do this?", "you want to put that here so much?", "Sorry, NO", "can you please just stop?", "please", "PLEEASE", "you know what?", "they do not pay me enough to do this", "goodbye", ""]
think_text = ["thinking...", "you cannot win", "you CAN'T win", "why are you even trying?", "give up before it is too late", "haha..."]
win_text = ["you lost... lol", "what did you expect?", "hey, its not that bad... I've won and you didnt", "...yay"]
draw_text = ["congrats, you are not stupid", "wanna play again?", "ugghhh", "this is boring", "I dare you to win"]

field = [0, 0, 0, 0, 0, 0, 0, 0, 0]
op = [0, 0]

###MINIMAX CONFIG###
WIN = 2
DRAW = 1
LOSE = 0

dp = [3] * 20000

no_count = 0


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

def thick_line(lcd, x, y, a, b, col):
    
    lcd.line(x + 1, y, a + 1, b, col)
    lcd.line(x, y, a, b, col)
    lcd.line(x - 1, y, a - 1, b, col)
    
    lcd.line(x, y + 1, a, b + 1, col)
    lcd.line(x, y, a, b, col)
    lcd.line(x, y + 1, a, b + 1, col)

def X(lcd, pos):
    x, y = pos
    thick_line(lcd, x, y, x + 18, y + 18, RED)
    thick_line(lcd, x + 18, y, x, y + 18, RED)

def O(lcd, pos):
    #this will be fucking difficult
    leg = 6
    hipo = 8
    
    x, y = pos
    
    thick_line(lcd, x + leg, y, x, y + leg, BLUE)
    thick_line(lcd, x, y + leg, x, y + leg + hipo, BLUE)
    thick_line(lcd, x, y + leg + hipo, x + leg, y + 2*leg + hipo, BLUE)
    thick_line(lcd, x + leg, y + 2*leg + hipo, x + leg + hipo, y + 2*leg + hipo, BLUE)
    thick_line(lcd, x + leg + hipo, y + 2*leg + hipo, x + 2*leg + hipo, y + leg + hipo, BLUE)
    thick_line(lcd, x + 2*leg + hipo, y + leg + hipo, x + 2*leg + hipo, y + leg, BLUE)
    thick_line(lcd, x + 2*leg + hipo, y + leg, x + leg + hipo, y, BLUE)
    thick_line(lcd, x + leg + hipo, y, x + hipo, y, BLUE)
    
    #ITS DONE!!

def display_field(lcd, fl):
    lcd.fill(BLACK)
    # 1) set 1 half of the screen white
    for i in range(0, 80):
        lcd.line(0, i, 80, i, WHITE)
    #DA GRID
    lcd.line(0, 27, 80, 27, BLACK)
    lcd.line(0, 54, 80, 54, BLACK)
    lcd.line(27, 0, 27, 80, BLACK)
    lcd.line(54, 0, 54, 80, BLACK)
    
    #now we display the data
    
    for i in range(len(fl)):
        if not fl[i]:
            continue
        x, y = ((i//3)*27, (i%3)*27)
        if fl[i] == 1:
            X(lcd, (x + 4, y + 4))
        else:
            #adjust a little
            O(lcd, (x + 4, y + 2))
    
    lcd.display()
def hover(lcd, pos, col):
    #27x27
    y, x = pos
    thick_line(lcd, x, y, x, y + 26, col)
    thick_line(lcd, x, y + 26, x + 26, y + 26, col)
    thick_line(lcd, x + 26, y + 26, x + 26, y, col)
    thick_line(lcd, x + 26, y, x, y, col)

def hover_game(lcd, fl, hover_pos, col):
    hover_pos = (hover_pos[0]*27, hover_pos[1]*27)
    display_field(lcd, fl)
    hover(lcd, hover_pos, col)
    lcd.display()

def text(lcd, your_text_here, col):
    for i in range(0, 75):
        lcd.line(85 + i, 0, 85 + i, 80, BLACK)
    words = your_text_here.split(' ')
    sentances = [""]
    max_ = 8
    for word in words:
        if len(sentances[-1]) + len(word) + 1 > max_:
            sentances.append(word)
        else:
            sentances[-1] += ' ' + word
    sentances[0] = sentances[0][1:]
    for i in range(len(sentances)):
        lcd.text(sentances[i], 85, i * 10 + 4, col)
    lcd.display()

def ask_user_input(lcd, fl):
    global no_count
    colors = [GREEN, RED]
    hover_game(lcd, fl, op, colors[int(field[op[1] * 3 + op[0]] != 0)])
    while True:
        if not KEY_UP.value():
            op[0] = max(op[0] - 1, 0)
            #ind = colors[int(field[op[0] * 3 + op[1]] != 0)]
            hover_game(lcd, fl, op, colors[int(field[op[1] * 3 + op[0]] != 0)])
            while not KEY_UP.value():
                continue
        elif not KEY_DOWN.value():
            op[0] = min(op[0] + 1, 2)
            hover_game(lcd, fl, op, colors[int(field[op[1] * 3 + op[0]] != 0)])
            while not KEY_DOWN.value():
                continue
        elif not KEY_RIGHT.value():
            op[1] = min(op[1] + 1, 2)
            hover_game(lcd, fl, op, colors[int(field[op[1] * 3 + op[0]] != 0)])
            while not KEY_RIGHT.value():
                continue
        elif not KEY_LEFT.value():
            op[1] = max(op[1] - 1, 0)
            hover_game(lcd, fl, op, colors[int(field[op[1] * 3 + op[0]] != 0)])
            while not KEY_LEFT.value():
                continue
        elif not KEY_CTRL.value():
            if field[op[1] * 3 + op[0]] == 0:
                return op[1] * 3 + op[0]
            else:
                print("okay")
                print(no_count)
                text(lcd, you_cannot[no_count], RED)
                print("dokay")
                no_count = min(no_count + 1, len(you_cannot) - 1)
            while not KEY_CTRL.value():
                continue

def generate_possibilities(br, player):
    possibilities = []
    for i in range(len(br)):
        if br[i] == 0:
            alt = [x for x in br]
            alt[i] = player
            possibilities.append(alt)
    return possibilities

def win(br, player):
    for i in range(3):
        if br[3*i] != 0 and br[3*i] == br[3*i + 1] and br[3*i] == br[3*i + 2]:
            if br[3*i] == player:
                return WIN
            else:
                return LOSE
    for i in range(3):
        if br[i] != 0 and br[i] == br[i + 3] and br[i] == br[i + 6]:
            if br[i] == player:
                return WIN
            else:
                return LOSE
    if br[0] != 0 and br[0] == br[4] and br[0] == br[8]:
        if br[0] == player:
            return WIN
        else:
            return LOSE
    if br[2] != 0 and br[2] == br[4] and br[2] == br[6]:
        if br[2] == player:
            return WIN
        else:
            return LOSE
    return DRAW

def full(fl):
    for el in fl:
        if el == 0:
            return False
    return True
def conv(s):
      ans = 0
      for c in map(int, s):
         ans = 3 * ans + c
      return ans

def assign_n(fl):
    n = 0
    for el in fl:
        n *= 10
        n += el
    return conv(str(n))
    

def ai(fl, player):
    if dp[assign_n(fl)] != 3:
        return dp[assign_n(fl)]
    e = win(fl, player)
    if e != DRAW:
        dp[assign_n(fl)] = e
        return e
    if full(fl):
        return DRAW
    opp_poss = generate_possibilities(fl, (player%2) + 1)
    opp_values = [ai(x, (player%2) + 1) for x in opp_poss]
    s = 2 - max(opp_values)
    dp[assign_n(fl)] = s
    return s

if __name__=='__main__':
    lcd = LCD_0inch96()
    display_field(lcd, field)
    pl = 1
    while True:
        text(lcd, random.choice(think_text), RED)
        boards = generate_possibilities(field, pl)
        values = [ai(x, pl) for x in boards]
        print ("done with generation, time for blood")
        field = boards[values.index(max(values))]
        display_field(lcd, field)
        
        if win(field, 1) == WIN:
            text(lcd, random.choice(win_text), RED)
            while True:
                continue
        if full(field):
            text(lcd, random.choice(draw_text), RED)
            while True:
                continue
        
        pl %= 2
        pl += 1
        
        pos = ask_user_input(lcd, field)
        field[pos] = pl
        pl %= 2
        pl += 1
        #ai time babyyyy
        display_field(lcd, field)
        
        if win(field, 1) == WIN:
            text(lcd, random.choice(win_text), RED)
            while True:
                continue
        if full(field):
            text(lcd, random.choice(draw_text), RED)
            while True:
                continue
        
    
        
    
