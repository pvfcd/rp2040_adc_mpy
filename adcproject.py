import machine
from machine import ADC, Pin,Timer
import utime
import st7789 as st7789
from fonts import vga2_8x8 as font1
from fonts import vga1_16x32 as font2
import math

ADC0_full_range =  65039
ADC1_full_range =  65535
ADC2_full_range =  64315
ADC3_full_range =  64719

"""pin设置部分"""
pinout = Pin(22, Pin.OUT)
calib = Pin(6, Pin.IN, Pin.PULL_UP)#即为板子上的按键A

'''ADC选择部分'''
# 排针
CH1 = ADC(Pin(26))     
CH2 = ADC(Pin(27))
adc	= 0	

# 摇杆 
# CH1 = ADC(Pin(28))     
# CH2 = ADC(Pin(29))
# adc = 1	

'''st7789设置部分'''
st7789_res = 0
st7789_dc  = 1
disp_width = 240
disp_height = 240
spi_sck=machine.Pin(2)
spi_tx=machine.Pin(3)
spi0=machine.SPI(0,baudrate=40000000, phase=1, polarity=1, sck=spi_sck, mosi=spi_tx)
display = st7789.ST7789(spi0, disp_width, disp_height,reset=machine.Pin(st7789_res, machine.Pin.OUT),dc=machine.Pin(st7789_dc, machine.Pin.OUT),xstart=0, ystart=0, rotation=0)

'''保存上一次指针位置部分'''
lastxposi = 0
lastyposi = 0
lastvalue = 0

'''测试用io口中断驱动程序'''
timer = Timer()
def timer_callback(timer):
	pinout.toggle()
timer.init(period=2000, mode=Timer.PERIODIC , callback=timer_callback)#创建一个定时器，用于反转电平





def adcread():
	global dmm1,dmm2

	# dmm1 = ADC(Pin(28))     
	# dmm2 = ADC(Pin(29))
	dmm1 = CH1.read_u16()    
	dmm2 = CH2.read_u16()


def adcshow():
	global dmm1voltshow,dmm2voltshow
	adcread()
	# print("dmm")
	# print(dmm1)
	# print(dmm2)
	if (adc == 0):
		dmm1volt = dmm1*(3.3/ADC0_full_range)
		dmm1voltshow = round(dmm1volt,3)
		dmm2volt = dmm2*(3.3/ADC1_full_range)
		dmm2voltshow = round(dmm2volt,3)
	else:
		dmm1volt = dmm1*(3.3/ADC2_full_range)
		dmm1voltshow = round(dmm1volt,3)
		dmm2volt = dmm2*(3.3/ADC3_full_range)
		dmm2voltshow = round(dmm2volt,3)
	print("volt")
	print(dmm1volt)
	print(dmm2volt)
	display.text(font2,"CH1:",0,10,st7789.WHITE)
	display.text(font2,"CH2:",0,40,st7789.WHITE)
	display.text(font2,str(dmm1voltshow),63,10,st7789.WHITE) 
	display.text(font2,str(dmm2voltshow),63,40,st7789.WHITE)
	# print("show")
	# print(dmm1voltshow)
	# print(dmm2voltshow)
	display.text(font2,"Volts",144,10)
	display.text(font2,"Volts",144,40)

def draw_point(value):
	'''
   value:ADC读取的电压值,例如32768之类的数字
	46811:adc满量程为3.3v分散到140的区域上,正好是表针的长度
	然后利用勾股定理,计算出y的位置
	'''
	global lastxposi,lastyposi,lastvalue
	tvalue = value*100
	# lastvalue = value
	# if (lastvalue <=0):
	# 	display.line(120,200,50,200,st7789.BLACK)
	if (value > 0):
		# print(value)
		if (adc == 0):
			xposi = (tvalue//(int((ADC0_full_range/140)*100)))+50
		else:
			xposi = (tvalue//(int((ADC2_full_range/140)*100)))+50
		if xposi != 0:
			yposi = 200-int((math.sqrt(4900-((120-xposi)**2))))
		else:
			yposi = 200
		# print(xposi,yposi)
		display.line(120,200,xposi,yposi,st7789.RED)
		if xposi != lastxposi:
			display.line(120,200,lastxposi,lastyposi,st7789.BLACK)
		lastxposi = xposi
		lastyposi = yposi
	# else:
		# display.line(120,200,50,200,st7789.RED)

if __name__ == '__main__':

	"""校准程序，开机按住a键（）即可进入校准"""
	if(calib.value() == 0):
		calib_bit = True
		while(calib_bit):
			ADC0 = ADC(Pin(26))
			ADC1 = ADC(Pin(27))
			ADC2 = ADC(Pin(28))
			ADC3 = ADC(Pin(29))
			display.fill(st7789.BLACK)
			display.text(font2,"input 3.3v",10,50,st7789.WHITE)

			# display.text(font2,"CALIB ADC0",10,10,st7789.WHITE)
			# while(ADC0.read_u16() <55000):
			# 	if(ADC0.read_u16() > 55000):
			# 		display.text(font2,"WAIT......",10,10,st7789.WHITE)
			# 		utime.sleep_ms(5000)
			# 		ADC0_full_range = ADC0.read_u16()
			# 		print("ADC0",ADC0_full_range)
			# 		break

			# display.text(font2,"CALIB ADC1",10,10,st7789.WHITE)
			# while(ADC1.read_u16() <55000):
			# 	if(ADC1.read_u16() > 55000):
			# 		display.text(font2,"WAIT......",10,10,st7789.WHITE)
			# 		utime.sleep_ms(5000)
			# 		ADC1_full_range = ADC1.read_u16()
			# 		print("ADC1",ADC1_full_range)
			# 		break

			display.text(font2,"CALIB ADC2",10,10,st7789.WHITE)
			while(ADC2.read_u16() <55000):
				if(ADC2.read_u16() > 55000):
					display.text(font2,"WAIT......",10,10,st7789.WHITE)
					utime.sleep_ms(5000)
					ADC2_full_range = ADC2.read_u16()
					print("ADC2",ADC2_full_range)
					break
			
			display.text(font2,"CALIB ADC3",10,10,st7789.WHITE)
			while(ADC3.read_u16() <55000):
				if(ADC3.read_u16() > 55000):
					display.text(font2,"WAIT......",10,10,st7789.WHITE)
					utime.sleep_ms(5000)
					ADC3_full_range = ADC3.read_u16()
					print("ADC3",ADC3_full_range)
					utime.sleep_ms(500)
					calib_bit =False
					break
			
			


	display.fill(st7789.BLACK)
	display.drawcircle(120,200,100)
	display.text(font1,"1.65v",100,110,st7789.WHITE)
	display.text(font1,"0v",25,200,st7789.WHITE)
	display.text(font1,"3.3v",180,200,st7789.WHITE)


		
		
		

	while(True):#主循环
		adcshow()
		draw_point(dmm1)

