import time,random,socket,os,math
import datetime
from Sensor import Dsensor
from spisender import spii
from multiprocessing import Queue as q, Process
from sys import argv

script,port=argv
port=int(port)
def f(que,que2,que3,i,d1):
    loghandle=open('log.txt','a')
    b=time.time
    vals=["Camera access","GPS","Velocity","Temp","Light","All","filename.fdx"]
    met=12001
    oldtime=time.time() #done to initalize
    def logeditor(loginfo):
        logdate=str(datetime.datetime.now())
        loginfo=str(loginfo)
        loghandle.write(logdate+"\t"+loginfo+"\n")
        loghandle.flush()
        
    #d1=Dsensor()
    #delt=0.0
    while i==0:### client side code
        try:
            met= met+1 if met < 13000 else 12001
            print("HELLO")

            def sixbitbytestring(bin24):
                p=chr(int(bin24[0:6],2)).encode() #the max interger value that can be encoded so that it takes up
                #one index is 127 so we'll divide our number. That is chr(128).encode() onwards you get two index string
                q=chr(int(bin24[6:12],2)).encode()#into 4 6 bit numbers, each 6 bit number we'll encode into a bytes type character string
                r=chr(int(bin24[12:18],2)).encode()#and append to the beginning of the data. so our metadata will take up 4 characters
                s=chr(int(bin24[18:24],2)).encode()
                return p+q+r+s

            def camera_sender(simage):
                n=0
                p=0
                camerafilename=(str(simage)).encode()
                print("Now sending file:",simage)
                connection.send(camerafilename)
                if n==0:
                    statinfo = os.stat(simage)
                    size=statinfo.st_size #gives the size of the file in bytes
                    totalbytes=format(math.ceil(size),'024b') #ceil function rounds up. Size is in bytes divided by 1024 bytes per packet gives
                    #number of packets
                    totalbytesEncoded=sixbitbytestring(totalbytes)
                    connection.send(totalbytesEncoded)
                    n=n+1
                f=open(simage,'rb')
                l=f.read(1024)
                while(l):
                    connection.send(l)
                    #print("Sending packet")
                    l=f.read(1024)
                print("TEST")
                f.close()
                print((connection.recv(1024)).decode())
                print('Done sending')

            server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #port=15005
            ip='192.168.0.5'
            server.bind((ip, port)) #server always needs to bind to its own ip adresss
            server.listen(5)
            while True:
                n=0
                connection, address = server.accept()
                print("TESTING!!")
                print('Got connection from', address)
                option=connection.recv(1024)
                doption=option.decode()
                ioption=int(doption)
                print("The selected option is",doption)
                #WE ALWAYS CONVERT THE DATA INTO STRNG AS IT IS EASY TO ENCODE AND SEND BACK TO THE CLIENT
                if(doption=='0'):
                    logeditor(doption)
                    que.put([met,ioption])
                    senimage=que2.get()
                    #print(senimage)
                    #camera_sender("image.bmp")
                    camera_sender(senimage[0])
                    camera_sender(senimage[1])
                elif(doption=='1'):
                    logeditor(doption)
                    que.put([met,ioption])
                    sgps=que2.get()
                    gpsdata=str(sgps[0])+" "+str(sgps[1])+" "+str(sgps[2])
                    egpsdata=gpsdata.encode()
                    connection.send(egpsdata)
                    print("GPS")
                elif(doption=='2'):
                    logeditor(doption)
                    que.put([met,ioption])
                    lvelocity=que2.get()
                    svelocity=str(lvelocity[0])+" "+str(lvelocity[1])+" "+str(lvelocity[2])
                    velocity=(str(svelocity)).encode()
                    print("Velocity")
                    connection.send(velocity)
                elif(doption=='3'):
                    logeditor(doption)
                    que.put([met,ioption])
                    stemperature=que2.get()
                    temperature=(str(stemperature)).encode()
                    connection.send(temperature)
                    print("Temperature")
                elif(doption=='4'):
                    logeditor(doption)
                    que.put([met,ioption])
                    slight=que2.get()
                    light=(str(slight)).encode()
                    connection.send(light)
                    print("Light")
                elif(doption=='5'):
                    logeditor(doption)
                    que.put([met,ioption])
                    sall=que2.get()
                    sallvelocity=sall[4]
                    svelco="Velocity: ["+str(sallvelocity[0])+" "+str(sallvelocity[1])+" "+str(sallvelocity[2])+"]"
                    sallimage=sall[0]
                    print("All sensor data")
                    print("Sending camera image data first")
                    camera_sender(sallimage[0])
                    camera_sender(sallimage[1])
                    connection.recv(1024) #we did this to clear the buffer
                    alldata=str(sall[1])+" "+str(sall[2])+" "+str(sall[3])+" "+svelco+" "+str(sall[5])+" "+str(sall[6])
                    alldataencoded=alldata.encode()
                    connection.send(alldataencoded)
                elif(doption=='6'):
                    logeditor(doption)
                    filename = connection.recv(1024).decode()
                    data=b'1'
                    print('The name of the file we will receive is:', filename)
                    connection.send(b'Filename Recevied by Server')
                    with open(filename, 'wb+') as f: #we need to change this empty.bmp to the variable filename
                        f.truncate()
                        print('The file on which we will write the receiving data has been opened on the pi')
                        while True:
                            print('RECEIVING DATA...............')
                            '''if n==0:
                                packetsEncoded=connection.recv(4)
                                print(packetsEncoded)
                                n=n+1
                                packetsDecoded=packetsEncoded[0]*2**18+packetsEncoded[1]*2**12+packetsEncoded[2]*2**6+packetsEncoded[3]*1
                                print("Total packets we will receive are:",packetsDecoded)
                                count=1''' #NO LONGER NEEDED as TCP sends the data in random amount of packets of different size but in correct oder
                            while data:#count<=packetsDecoded:
                                data = connection.recv(1024)
                                #data=data.decode()
                                #print('data=',data)
                                #count=count+1
                                f.write(data)
                            f.close()
                            break
                        que.put([met,ioption,filename])
                elif(doption=='7'):
                    logeditor(doption)
                    camera_sender('log.txt')
        except Exception as e:
            print(e)
            logeditor(e)
    while i==1: ### main prog code
        try:
            newtime=time.time()
            if newtime-oldtime>5:
                d1.Dvelocity()
                oldtime=newtime
            else:
                if que.empty():
                    pass
                else:
                    v=que.get()
                    if v[1]==0:
                        d1.Dcamera()
                        que2.put(d1.dimage)
                    elif v[1]==1:
                        que2.put([d1.dlatitude,d1.dlongitude,d1.dtime])
                    elif v[1]==2:
                        que2.put(d1.dvelocity)
                    elif v[1]==3:
                        d1.Dtemperature()
                        que2.put(d1.dtemp)
                    elif v[1]==4:
                        d1.Dlight()
                        que2.put(d1.dlight)
                    elif v[1]==5:
                        d1.Update()
                        que2.put([d1.dimage,d1.dlatitude,d1.dlongitude,d1.dtime,d1.dvelocity,d1.dtemp,d1.dlight])
                    elif v[1]==6:
                        que3.put(v[2])
        except Exception as e:
            print(e)
            logeditor(e)
    while i==2:        ### SPI code
        try:
            w=que3.get()
            print(w)
            while que3.empty():
                spii(w)
        except Exception as e:
            print(e)
            logeditor(e)

if __name__ == "__main__":
    procs=[]
    #val=[0,1]
    print("starting")
    q1=q() # server to main
    q2=q() # main to SERVER
    q3=q() # main to SPI
    d1=Dsensor()
    try:
        for val in [0,1,2]:
            proc=Process(target=f,args=(q1,q2,q3,val,d1,))
            procs.append(proc) #this is for debugging purposes, useful if one process stops working, shows us whats wrong
            proc.start()
    except KeyboardInterrupt:
        exit()


