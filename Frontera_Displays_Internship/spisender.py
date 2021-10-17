#we need to send spi data, that is one frame in 4ms, so spi max transfer is 4096 bytes. We can send 8 rows at once which is 288**=2304 characters
#if this sends in under 4ms, we need to send 0s for the rest of the time. Tf 4ms reached send new data
#since the logic analyzer can't keep up with the speed we want, for now we want a frame to be 80 ms and clock frequency 97600


import spidev
import time
import newbinimp

def spii(file):
    spi = spidev.SpiDev() #create spi object
    spi.open(0, 1)
    #open spi port 0, device (CS) 1
    spi.max_speed_hz = 15600000
    fname=file
    fhandle=open(fname,'rb')
    order=list()
    j=1
    k=1
    i=1
    totalpixels=192
    totalrows=64
    spacing=int(totalrows/4) #this gives 16 for 64
    while j<(spacing+1): #this is as long as j<16+1=17
        order.extend((j,j+spacing,j+spacing*2,j+spacing*3))#this is 1,17,33,49 and so on
        j=j+1
    #print(order)
    final=list()
    for k in order: #this obtains a list of all charcters in the file in the order 1,17,33,49,2,18 and so on
        inital=newbinimp.extract(fhandle,totalpixels,k)
        final.append(newbinimp.metdat(inital,totalpixels,k))
        k+1
    spidatainlistform=list()
    for i in range(len(final)): #this obtains the previous char data and converts each row to a list of numbers so we get[[data in row1],[data in row 17]] and son
        spidatainlistform.append([ord(x) for x in final[i]])
    i=0
    #print(spidatainlistform)
    spidata=[] #this converts it into one big list of 291*64=18624 numbers
    while(i<totalrows): #the total rows are 64
        spidata=spidata+spidatainlistform[i]
        i=i+1
    #print(spidata)


    #we are sending 8 rows at a time so we are sending therefore 8*291 characters which is 2328

    charsatatime=(int(totalpixels*12/8)+3)*8 #this value is 192*12/8=288+3=291*8=2328

    #we now need to append 0's to our spidata so that we send total of 4096 characters which is max packet buffer allowed by spi module
    #4096-2328=1768
    #listofappendedzeros=list()
    #for i in range(4096-charsatatime):
        #listofappendedzeros.append(0)
    #print(len(listofappendedzeros))

    ###NO NEED TO APPEND ZEROS BECAUSE WE CHANGED THE CONFIGURATION OF THE ENABLE TO BE HIGH ONLY WHEN DATA IS BEING SENT

    listofzeros=list() #we also need a null list of 4096 listofzeros
    for i in range(4096):
        listofzeros.append(0)

    #print(len(listofzeros))
    #print(spidata[charsatatime:charsatatime*2]+listofappendedzeros)
    #print(len(spidata[charsatatime:charsatatime*2]+listofappendedzeros))

    while True:
        for i in range(int(totalrows/8)): #we are sending 8 rows at a time so 64/8 is 8
            a=time.time()
            spi.cshigh= True #False configures the spi enable to be high in the normal state and when data needs to be sent it pulls the line to low
            #when this is True it cnfigures the spi enable to be low in normal state and when data needs to be sent it makes it high (this is permanent)
            spi.writebytes(spidata[charsatatime*i:charsatatime*(i+1)])
            spi.no_cs=True #now since chip select is active high, this makes it low
            b=time.time()
            T=4*10**(-3) #fpga reads the frame every 4ms but since our clock speed is low initally, weve done it for 80
            while(b-a<T):
                if(T-(b-a)>(4096*8/spi.max_speed_hz)): #4096 total bytes we can send, 8 is number of bits in a byte dividing by clock frequency gives time period of one packet=33ms
                    spi.writebytes2(listofzeros)#if the remaining time is greater than the time period of one packet, we send an entire packet of zeros
                elif (T-(b-a)<(4096*8/spi.max_speed_hz)):
                    #if the remaing time(T-(b-a) is less we send the amount of character that can be encoded in the remaing time which
                    spi.writebytes2([0] *int((T-(b-a))*spi.max_speed_hz/8))
                    spi.no_cs= False #since now chip select is active high, this makes the chip select high just beore the next packet of 8 rows is sent
                #print("initial", T-(b-a))
                b=time.time()
                #print("final", T-(b-a))

    #we have configured so that when data is sent, the enable is high. The enable is therefore only high for the 8 rows. For the zeros
    #the enable is off            