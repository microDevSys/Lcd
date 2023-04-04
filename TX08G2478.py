# Test 16bits LCD with GPIO
# author : Guillaume Sahuc
# test of S6D04D1X21 240*432

from RPi import GPIO
from time import sleep
from color import *
from StarField import *

# suppresses warnings on RasPi
GPIO.setwarnings(False)
# configure the GPIO
GPIO.setmode(GPIO.BCM)

# define a x bits data bus
IO8 = (25, 8, 7, 1, 12, 16, 20, 21)  # MSB to LSB
IO16 = (4, 3, 2, 14, 15, 18, 23, 24, 25, 8, 7, 1, 12, 16, 20, 21)  # MSB to LSB
LCD_BUS = (26, 19, 13, 6 , 5)
LCD_RESET = 26
LCD_CS = 19
LCD_RS = 13
LCD_WR = 6
LCD_RD = 5


# -----------------------------
# ---------SETUP GPIO----------
# -----------------------------
for bit in IO16:
    GPIO.setup(bit, GPIO.OUT)
for bit in LCD_BUS:
    GPIO.setup(bit, GPIO.OUT)

# ----------------------------
# ---------CLEAR PIN----------
# ----------------------------

def clear_reset():
    GPIO.output(LCD_RESET, 0)

def clear_CS():
    GPIO.output(LCD_CS, 0)

def clear_RS():
    GPIO.output(LCD_RS, 0)

def clear_WR():
    GPIO.output(LCD_WR, 0)

def clear_RD():
    GPIO.output(LCD_RD, 0)

# ----------------------------
# ---------SET PIN------------
# ----------------------------

def set_reset():
    GPIO.output(LCD_RESET, 1)

def set_CS():
    GPIO.output(LCD_CS, 1)

def set_RS():
    GPIO.output(LCD_RS, 1)

def set_WR():
    GPIO.output(LCD_WR, 1)

def set_RD():
    GPIO.output(LCD_RD, 1)
# ----------------------------
# ---------CLEAR BUS----------
# ----------------------------
def clear_bus(bus):
    for pin in bus:
        GPIO.output(pin, 0)

# ----------------------------
# ---------SET BUS------------
# ----------------------------

def set_8bits_bus(bus, data):  # data must be a hexadecimal like 0xff
    bits = "{0}".format(bin(data))[2:]  # binary value of data
    bits = "{0:0>8}".format(bits)  # force 8 bits value
    for x in range(len(bits)-1, -1, -1):  # start LSB to MSB
        GPIO.output(bus[x], int(bits[x]))  # LSB first to MSB

def set_16bits_bus(bus, data):  # data must be hexadecimal like 0xffff
    bits = "{0}".format(bin(data))[2:]  # binary value of data
    bits = "{0:0>16}".format(bits)  # force 16 bits value
    for x in range(len(bits)-1, -1, -1):  # start LSB to MSB
        GPIO.output(bus[x], int(bits[x]))  # LSB first to MSB

def Color24to16(color):
    #color conversion 24bits to 16bits
    color = ((( color >> 8) & 0xF800) |((color >> 5) & 0x7E0) | \
    ((color >> 3) & 0x1F))
    return color

class Lcd(object):


    def Write_Com_8(self,data):
        clear_CS()
        clear_RS()
        set_8bits_bus(IO8, data)
        clear_WR()
        set_WR()
        set_RS()
        set_CS()

    def Write_DATA_8(self,data):
        clear_CS()
        set_RS()
        set_8bits_bus(IO8, data)
        clear_WR()
        set_WR()
        set_CS()

    def Write_DATA_16(self,data):
        clear_CS()
        set_RS()
        set_16bits_bus(IO16, data)
        clear_WR()
        set_WR()
        set_CS()

    def Address_set(self,x1, y1, x2, y2):
        self.Write_Com_8(0x2A) #Set_column_address
        self.Write_DATA_8(x1>>8)
        self.Write_DATA_8(x1&0xFF)
        self.Write_DATA_8(x2>>8)
        self.Write_DATA_8(x2&0xFF)

        self.Write_Com_8(0x2B)  #Set_row_address
        self.Write_DATA_8(y1>>8)
        self.Write_DATA_8(y1&0xFF)
        self.Write_DATA_8(y2>>8)
        self.Write_DATA_8(y2&0xFF)

        self.Write_Com_8(0x2C)  # write memory start

    def SetPixel(self,x, y, color):
        self.Address_set(x,y,x,y)
        self.Write_DATA_16(color)

    def Fill(self,color):
        self.Address_set(0x00, 0x00, 239, 431)
        set_16bits_bus(IO16, color)
        clear_CS()
        for x in range(0,240):
            for y in range(0,432):
                clear_WR()
                set_WR()
        set_CS()

    def Fill_H(self,color):
        self.Write_Com_8(0x36)
        self.Write_DATA_8(0x28)
        self.Address_set(0x00, 0x00, 431, 239)
        set_16bits_bus(IO16, color)
        clear_CS()
        for x in range(0,432):
            for y in range(0,240):
                clear_WR()
                set_WR()
        set_CS()
        self.Write_Com_8(0x36)
        self.Write_DATA_8(0x48)

    def Fill_Box(self,x, y, width, height,color):
        self.Address_set(x,y,width, height)
        for i in range(0,height+1):
            set_16bits_bus(IO16, color)
            for j in range(0,width+1):
                clear_CS()
                clear_WR()
                set_WR()
            self.Address_set(x,y+i,239, 431)
        set_CS()

    def Line(self,x0,y0,x1,y1,color):
        dy = y1 - y0
        dx = x1 - x0
        if ((dy == 0) & (dx == 0)):
            self.SetPixel(x0,y0,color)
            return
        elif (dy == 0):
            self.Fill_Box(x0,y0,x1,1,color)
            return
        elif (dx == 0):
            self.Fill_Box(x0,y0,0,y1,color)
            return
        else :
            m = float(dy / dx)
            b = y0 - int(m * x0)
        self.Address_set(0, 0, 239, 431)

        if (abs(dx) >= abs(dy)):
            if (x0 > x1):
                x0, x1 = x1, x0 # swap
                y0, y1 = y1, y0 # swap
            while( x0 <= x1):
                self.SetPixel(x0, y0, color)
                x0 += 1
                if (x0 <= x1):
                    y0 = int(m * x0) + b
        else :
            if  ( y0 > y1 ):
                x0, x1 = x1, x0 # swap
                y0, y1 = y1, y0 # swap
            while(y0 <= y1):
                self.SetPixel(x0, y0, color)
                y0 += 1
                if ( y0 <= y1):
                    if(dx != 0):
                        x0 = int((y0 - b)/ m)

    def Circle(self, x0, y0, radius, color):
        D = radius - 1
        curX = 0
        curY = radius
        while(curY >= curX):
            self.SetPixel(x0 + curX, y0 + curY, color)
            self.SetPixel(x0 + curX, y0 - curY, color)
            self.SetPixel(x0 - curX, y0 + curY, color)
            self.SetPixel(x0 - curX, y0 - curY, color)
            self.SetPixel(x0 + curY, y0 + curX, color)
            self.SetPixel(x0 + curY, y0 - curX, color)
            self.SetPixel(x0 - curY, y0 + curX, color)
            self.SetPixel(x0 - curY, y0 - curX, color)
            if ( D >= 2 * curX):
                D = D - 2 * curX -1
                curX += 1
            elif (D <= (2*(radius-curY))) :
                D = D + 2 * curY - 1
                curY += -1
            else:
                D += 2 * (curY - curX - 1)
                curY += -1
                curX += 1

    def Fill_Circle(self, x0, y0, radius, color):
        while(radius >=0):
            self.Circle(x0,y0,radius,color)
            radius += -1

    def __init__(self):
        clear_reset()
        set_RD()
        sleep(0.01)
        set_reset()
        sleep(0.1)
        self.Write_Com_8(0x01) # software reset
        sleep(0.1)
        self.Write_Com_8(0x11) # exit sleep mode
        sleep(0.1)
        self.Write_Com_8(0xF4)  # Vcom control register
        self.Write_DATA_8(0x59)
        self.Write_DATA_8(0x57)
        self.Write_DATA_8(0x57)
        self.Write_DATA_8(0x11)

        self.Write_Com_8(0xF5)  # Source Output Control Register
        self.Write_DATA_8(0x12)
        self.Write_DATA_8(0x00)
        self.Write_DATA_8(0x0B)
        self.Write_DATA_8(0xF0)
        self.Write_DATA_8(0x00)

        self.Write_Com_8(0xF3)  #  Power Control Register
        self.Write_DATA_8(0xFF)
        self.Write_DATA_8(0x2A)
        self.Write_DATA_8(0x2A)
        self.Write_DATA_8(0x07)
        self.Write_DATA_8(0x22)
        self.Write_DATA_8(0x57)
        self.Write_DATA_8(0x57)
        self.Write_DATA_8(0x20)

        self.Write_Com_8(0xF2)  #  Display Control Register
        self.Write_DATA_8(0x0E)
        self.Write_DATA_8(0x14)
        self.Write_DATA_8(0x00)
        self.Write_DATA_8(0x08)
        self.Write_DATA_8(0x08)
        self.Write_DATA_8(0x08)
        self.Write_DATA_8(0x08)
        self.Write_DATA_8(0x00)
        self.Write_DATA_8(0x04)
        self.Write_DATA_8(0x1A)
        self.Write_DATA_8(0x1A)

        self.Write_Com_8(0xF6)  #  Interface Control Register
        self.Write_DATA_8(0x00)
        self.Write_DATA_8(0x00)
        self.Write_DATA_8(0x80)
        self.Write_DATA_8(0x10)

        self.Write_Com_8(0xFD)  #  Gate Control Register
        self.Write_DATA_8(0x11)
        self.Write_DATA_8(0x00)

        self.Write_Com_8(0x13) # partial mode off ( normal mode )
        self.Write_Com_8(0x20) # inversion off

        self.Write_Com_8(0x36)  # Set_address_mode
        self.Write_DATA_8(0x48)

        self.Write_Com_8(0x3A)  # Set_pixel_format
        self.Write_DATA_8(0x55) # 16bit/pixel

        self.Write_Com_8(0x29) # Lcd ON

if __name__ == "__main__":
    Lcd = Lcd()
    Lcd.Fill(Color24to16(color.red))
    Lcd.Fill(Color24to16(color.blue))
    Lcd.Fill_H(Color24to16(color.red))
    Lcd.Fill_H(Color24to16(color.blue))
    Lcd.Fill(Color24to16(color.black))
    Lcd.Line(0,0,239,0,Color24to16(color.red))
    Lcd.Line(0,0,0,431,Color24to16(color.red))
    Lcd.Line(0,431,239,431,Color24to16(color.red))
    Lcd.Line(239,0,239,431,Color24to16(color.red))
    Lcd.Line(0,0,239,431,Color24to16(color.red))
    Lcd.Line(239,0,0,431,Color24to16(color.red))
    Lcd.Fill_Circle(120,108,20,Color24to16(color.blue))
    Lcd.Fill_Circle(120,324,20,Color24to16(color.red))
    init.Star()
    Lcd.Fill(Color24to16(color.black))
    while(1):
        for star in Stars.ListOfStar:
            star.y += star.speed
            if star.y > 431:
                star.y = 0
            Lcd.SetPixel(star.last_x,star.last_y,Color24to16(color.black))
            Lcd.SetPixel(star.x,star.y,Color24to16(color.white))
            star.last_x = star.x
            star.last_y = star.y