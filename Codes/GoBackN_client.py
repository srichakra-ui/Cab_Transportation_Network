from socket import *
import time
import random
def GBNsend(conn,message):
    conn.send(str(len(message)).encode())
    time.sleep(1)
    i=0
    frames=len(message)
    print("No of frames to be sent:",frames)
    wsize=int(input("Enter the sliding window size:"))
    # wsize=4
    ack=""
    wsize=wsize-1
    k=wsize
    while i!=frames:
        while(i!=(frames-wsize)):
            conn.send(message[i].encode())
            ack=conn.recv(1024)
            ack=ack.decode()
            print(ack)
            if(ack!="ACK Lost"):
                print("ACK Received!")
                print("The sliding window range:"+(str(i+1))+" to "+str(k+1)+"")
                print("Sending the next packet")
                i=i+1
                k=k+1
            else:
                print("ACK of the data bit "+(str(i))+" is LOST!")
                print("The sliding window remains in the range "+(str(i))+" to "+str(k)+"")
                print("Now Resending all packets from "+(str(i))+" to "+(str(k))+"")
            time.sleep(0.1)
        while(i!=frames):
            conn.send(message[i].encode())
            ack=conn.recv(1024)
            ack=ack.decode()
            print(ack)
            if(ack!="ACK Lost"):
                print("ACK Received!")
                print("The sliding window range "+(str(i+1))+" to "+str(k)+"")
                if(i<frames-1):
                    print("Sending the next packet")
                i=i+1
            else:
                print("ACK of the data bit "+(str(i))+" is LOST!")
                print("The sliding window remains in the range "+(str(i))+" to "+str(k)+"")
                print("Now Resending all packets from "+(str(i))+" to "+(str(k))+"")
            time.sleep(0.1)

def GBNrecv(connection):
    k=connection.recv(2048).decode()
    # print(k,'len of msg')
    k=int(k)
    i=0
    originalmsg=''
    ack=''
    f=random.randint(0,1)
    nxtchr=''
    while i!=k:
        f=abs(random.randint(0,1) - random.randint(0,1))
        if(f==0):
            ack='ACK '+str(i)
            nxtchr = connection.recv(1024)
            nxtchr = nxtchr.decode()
            # print(nxtchr)
            connection.send(ack.encode())
            originalmsg=originalmsg+nxtchr
            i=i+1
        else:
            ack='ACK Lost'
            nxtchr = connection.recv(1024)
            nxtchr = nxtchr.decode()
            connection.send(ack.encode())
    # print('The message received is :', originalmsg)
    return originalmsg

tcp_soc = socket(AF_INET, SOCK_STREAM)
sendAddr = ('localhost', 3000)
tcp_soc.connect(sendAddr)
msg  = tcp_soc.recv(2048).decode()
# msg=GBNrecv(tcp_soc)
print(msg+'\n')
while True:
    print('Enter choice: 1)Rent 2)Return 3)Generate Bill or any other number to exit')
    ip=int(input())
    if ip==1:
        cname='start'
    elif ip==2:
        cname='end'
    elif ip==3:
        cname='bill'
    else:
        exit(0)

    if ip==1:
        print('Enter Start location:')
        loc=input().strip()
        print('Enter Destination:')
        dest=input().strip()
        command=cname+' '+loc+' '+dest
    if ip==2:
        print('Enter Destination:')
        loc=''
        dest=input().strip()
        command=cname+' '+loc+' '+dest
    if ip==3:
        print('Enter the start,drop locations and distance travelled:')
        dist=input()
        command=cname+' '+dist

    # tcp_soc.send(command.encode())
    GBNsend(tcp_soc,command)
    # l = tcp_soc.recv(2048).decode()
    l=GBNrecv(tcp_soc)
    print(l)
tcp_soc.close()