def extract(fhandle,pix,row):
    fhandle.seek(0)
    whiteString=fhandle.read()
    npix=int(pix)
    amountofchar=int(npix*12/8)#int done here as when you do division it takes as float
    extract=whiteString[amountofchar*(row-1):amountofchar*(row)]
    blist=list(extract) #to convert bytes type string into character string we need to convert to list first
    extract=""
    for i in range(amountofchar):
        extract=extract+chr(blist[i])
    #print(extract)
    return extract

def metdat(datarow,pix,row):
    x=format(int(pix)+2,'012b')#this converts the value into a 12 bit binary number with 0's appended in the form of a string
    #we added +2 because total 12 bit packets being sent are the 12 bit 192 pixels and 12 bits for row number and 12 bits for total packets=192 12 bit packets + 2 more for metadata
    y=format(int(row),'012b')
    z=x+y#the concatenated meta data
    #print(z)
    a=chr(int(z[0:8],2)) #this takes the first 8 index in the string, converts to integer and finally converts it to a char
    #print(a)
    b=chr(int(z[8:16],2))
    #print(b)
    c=chr(int(z[16:24],2))
    #print(c)
    finrow=a+b+c+datarow
    #print("The metaata added gives",finrow)
    return finrow
 #onepixel represents 12 bits on the fpga