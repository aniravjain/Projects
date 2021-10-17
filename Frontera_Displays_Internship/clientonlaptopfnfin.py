import socket
import os
import math,time

def clientfrontera(host,port,b):
    b=str(b)
    def sixbitbytestring(bin24):
        p=chr(int(bin24[0:6],2)).encode() #the max interger value that can be encoded so that it takes up
        #one index is 127 so we'll divide our number. That is chr(128).encode() onwards you get two index string
        q=chr(int(bin24[6:12],2)).encode()#into 4 6 bit numbers, each 6 bit number we'll encode into a bytes type character string
        r=chr(int(bin24[12:18],2)).encode()#and append to the beginning of the data. so our metadata will take up 4 characters
        s=chr(int(bin24[18:24],2)).encode()
        return p+q+r+s

    def camera_receiver():
        n=0
        ibs=0
        initial=client.recv(1024)
        camerafilename=initial.decode()
        print("The name of the file we will receive is", camerafilename)
        with open(camerafilename, 'wb+') as f: #b specifies writiing in bytes,+ specifies to create that file as well
            #replace random.bmp with camerafilename
            f.truncate()
            print('file opened')
            while True:
                print('receiving data...')
                if n==0:
                    bytesEncoded=client.recv(4)
                    print(bytesEncoded)
                    n=n+1
                    bytesDecoded=bytesEncoded[0]*2**18+bytesEncoded[1]*2**12+bytesEncoded[2]*2**6+bytesEncoded[3]*1
                    print("Total bytes we will receive are:",bytesDecoded)
                while ibs<bytesDecoded:
                    #data=None
                    data = client.recv(1024)
                    f.write(data)
                    ibs=ibs+len(data)
                    print(data)
                    #print("packet: ",count)
                    #count=count+1
                f.close()
                client.send(b'Client has finished receving the data') #to clear buffer
                print("DONE RECEIVING THE CAMERA FILE")
                return 0

    def log_receiver():
        n=0
        ibs=0
        initial=client.recv(1024)
        camerafilename=initial.decode()
        print("The name of the file we will receive is", camerafilename)
        with open(camerafilename, 'w+') as f:
            f.truncate()
            print('file opened')
            while True:
                print('receiving data...')
                if n==0:
                    bytesEncoded=client.recv(4)
                    print(bytesEncoded)
                    n=n+1
                    bytesDecoded=bytesEncoded[0]*2**18+bytesEncoded[1]*2**12+bytesEncoded[2]*2**6+bytesEncoded[3]*1
                    print("Total bytes we will receive are:",bytesDecoded)
                while ibs<bytesDecoded:
                    data = (client.recv(1024)).decode()
                    f.write(data)
                    ibs=ibs+len(data)
                    print(data)
                f.close()
                client.send(b'Client has finished receving the data') #to clear buffer
                print("DONE RECEIVING THE CAMERA FILE")
                return 0

    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #host='192.168.0.5'
    #port=15,005
    client.connect((host,port))
    #b=input("Select the option:\n 0 Camera Access\n 1 GPS\n 2 Velocity\n 3 Temperature\n 4 Light\n 5 All Sensor Data\n 6 Send File\n")
    if(b=='0'):
        client.send(b.encode())
        camera_receiver()
        camera_receiver()
    elif(b=='1'):
        client.send(b.encode())
        print(client.recv(1024).decode())
    elif(b=='2'):
        client.send(b.encode())
        print(client.recv(1024).decode())
    elif(b=='3'):
        client.send(b.encode())
        print(client.recv(1024).decode())
    elif(b=='4'):
        client.send(b.encode())
        print(client.recv(1024).decode())
    elif(b=='5'):
        client.send(b.encode())
        camera_receiver()
        camera_recevier()
        client.send(b'Send rest of the data') #done to clear the buffer
        print("Now receving the gps data, velocity data, temperature data, and light data respectively: ")
        print(client.recv(1024).decode())
    elif(b=='6'):
        client.send(b.encode())
        filename='white.txt'
        client.send(filename.encode()) #hello seerver line
        print(client.recv(1024).decode())
        n=0
        '''if n==0:
            statinfo = os.stat(filename)
            size=statinfo.st_size #gives the size of the file in bytes
            totalpackets=format(math.ceil(size/1024),'024b') #ceil function rounds up. Size is in bytes divided by 1028 bytes per packet gives
            #number of packets
            totalpacketsEncoded=sixbitbytestring(totalpackets)
            print(totalpacketsEncoded)
            client.send(totalpacketsEncoded)
            n=n+1'''
        f=open(filename,'rb')
        #f.seek(0)
        l=f.read(1024)
        while(l):
            client.send(l)
            l=f.read(1024)
        f.close()
        client.close()
        print("Done sending")
    elif(b=='7'):
        client.send(b.encode())
        log_receiver()
