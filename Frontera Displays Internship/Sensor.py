import time,serial,sys,pygame,pygame.camera,datetime
from math import cos,sin,acos
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO
import time
   
class Dsensor:
    def __init__(self):
        self.dtemp=0.0
        self.dlight=""
        self.dimage=["",""]
        self.dvelocity=[0,0,0]   
        self.Dgps() #we do this to initalize dlatitude,dlongitude,dtime,and dcalcseconds
        self.dvelcdata=[self.dlatitude,self.dlongitude,self.dcalcseconds]

        

    def Dtemperature(self):
        tsensor=W1ThermSensor()
        temperature=tsensor.get_temperature()
        
        self.dtemp=temperature

    def Dlight(self):
        mpin=17
        tpin=27
        GPIO.setmode(GPIO.BCM)
        cap=0.0000047
        adj=2.130620985
        i=0
        t=0
        GPIO.setup(mpin, GPIO.OUT)
        GPIO.setup(tpin, GPIO.OUT)
        GPIO.output(mpin, False)
        GPIO.output(tpin, False)
        time.sleep(0.2)
        GPIO.setup(mpin, GPIO.IN)
        time.sleep(0.2)
        GPIO.output(tpin, True)
        starttime=time.time()
        endtime=time.time()
        while (GPIO.input(mpin) == GPIO.LOW):
            endtime=time.time()
        measureresistance=endtime-starttime
        res=(measureresistance/cap)*adj
        print(res)
        if res<=600:
            self.dlight="Bright"
        elif 600<res<=1300:
            self.dlight="Normal"
        elif 1300<res<3200:
            self.dlight="Dim"
        else:
            self.dlight="Dark"


    def Dgps(self):
        
        def ist_and_calctime(nmeatime):
            nmeahours=int(nmeatime[0:2])
            nmeaminutes=int(nmeatime[2:4])
            nmeaseconds=int(nmeatime[4:6])
            
            istseconds=nmeaseconds
            istminutes=nmeaminutes+30
            if(istminutes>=60):
                istminutes=istminutes-60
                nmeahours=nmeahours+1
            
            isthours=nmeahours+5
            calchours=isthours
            if(isthours>=24):
                isthours=isthours-24
            
            print("The time is",isthours,":",istminutes,":",istseconds)
            isttime=str(isthours)+":"+str(istminutes)+":"+str(istseconds)
            timeinseconds=calchours*60*60+istminutes*60+istseconds
            return isttime,timeinseconds
        
        def GPS_Info(NMEA_buff):
            nmea_time = []
            nmea_latitude = []
            nmea_longitude = []
            nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
            nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
            nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
            
            a,b=ist_and_calctime(nmea_time)
            self.dtime=a
            self.dcalcseconds=b
            #print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
            
            lat = float(nmea_latitude)                  #convert string into float for calculation
            longi = float(nmea_longitude)               #convertr string into float for calculation
            
            lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
            long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format
            
            return lat_in_degrees,long_in_degrees
            
        def convert_to_degrees(raw_value):
            decimal_value = raw_value/100.00
            degrees = int(decimal_value)
            mm_mmmm = (decimal_value - int(decimal_value))/0.6
            position = degrees + mm_mmmm
            position = "%.4f" %(position)
            return position
        
        gpgga_info = "$GPGGA,"
        ser = serial.Serial ("/dev/ttyS0")              #Open port with baud rate
        GPGGA_buffer = 0
        NMEA_buff = 0
        lat_in_degrees = 0
        long_in_degrees = 0
        
        received_data = (str)(ser.readline())#read NMEA string received
        #print(received_data)
        while not received_data.startswith("b'$GPGGA"): #keeps reading the pin till it recevies the data in the correct format
            received_data= (str)(ser.readline())
        GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string
        #print(GPGGA_data_available)
        if (GPGGA_data_available>0):
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string
            NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
            lat_in_degrees,long_in_degrees=GPS_Info(NMEA_buff) #get time, latitude, longitude
            self.dlatitude=lat_in_degrees
            self.dlongitude=long_in_degrees
            print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')

        

    def Dvelocity(self):
        def distbetween(lat1,lon1,lat2,lon2):
            lat1=float(lat1)*3.1415/180.0
            lon1=float(lon1)*3.1415/180.0
            
            lat2=float(lat2)*3.1415/180.0
            lon2=float(lon2)*3.1415/180.0
            
            r=6378100
            
            rho1=r*cos(lat1)
            z1=r*sin(lat1)
            x1=rho1*cos(lon1)
            y1=rho1*sin(lon1)
            
            rho2=r*cos(lat2)
            z2=r*sin(lat2)
            x2=rho2*cos(lon2)
            y2=rho2*sin(lon2)
            
            dot=x1*x2+y1*y2+z1*z2
            cos_theta=dot/(r*r)
            if cos_theta>=1:
                cos_theta=1
            #print(cos_theta)
            theta=acos(cos_theta)
            distance=r*theta  #distance in meters
            
            return distance
        
        self.Dgps()
        dist=distbetween(self.dvelcdata[0],self.dvelcdata[1],self.dlatitude,self.dlongitude)
        velc=dist/(self.dcalcseconds-self.dvelcdata[2])
        self.dvelocity[0]=self.dvelocity[1]
        self.dvelocity[1]=self.dvelocity[2]
        self.dvelocity[2]=velc
        self.dvelcdata=[self.dlatitude,self.dlongitude,self.dcalcseconds]

    def Dcamera(self):
        pygame.init()
        pygame.camera.init()
        date_timei=str(datetime.datetime.now())
        date_time=date_timei[0:19]
        date_time=date_time.replace(':','')
        cam=pygame.camera.Camera("/dev/video0")
        cam2=pygame.camera.Camera("/dev/video1")
        
        cam.start()
        cam2.start()
        
        image=cam.get_image()
        image2=cam2.get_image()
        
        cam.stop()
        cam2.stop()
        
        imagename1="img1_"+date_time+".jpg"
        imagename2="img2_"+date_time+".jpg"
        pygame.image.save(image,imagename1)
        pygame.image.save(image2,imagename2)

        self.dimage[0]=imagename1
        self.dimage[1]=imagename2
        
        
    def Update(self):
        self.Dtemperature()
        self.Dlight()
        #self.Dgps()
        self.Dcamera()
        #self.Dvelocity()
