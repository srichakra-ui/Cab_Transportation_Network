from socket import *
import math
import datetime
import os
import time
import random
from _thread import *


def SRrecv(conn):
    k=conn.recv(2048).decode()
    k=int(k)
    i=0
    orig_msg=[""] * (k-1)
    b=""
    ack=[]
    f=random.randint(0,1)
    message=""
    while(i!=4):
        message = conn.recv(1024).decode()
        orig_msg[i] = message
        # print(message)
        ack.append(i)
        i+=1
    while i!=k-1:
        f=abs(random.randint(0,1) - random.randint(0,1))
        if(f==0):
            b="ACK "+str(ack[0])
            conn.send(b.encode())
            message = conn.recv(1024).decode()
            # print(message)
            orig_msg[i] = message
            ack.append(i)
            ack.pop(0)
            i=i+1

        else:
            b="ACK Lost"
            conn.send(b.encode())
            message = conn.recv(1024)
            message = message.decode()
            orig_msg[ack[0]] = message
    while(len(ack) != 0):
        b="ACK "+str(ack[0])
        conn.send(b.encode())
        ack.pop(0)
        i+=1
        time.sleep(0.5)
    conn.send('Final ACK'.encode())
    return ''.join(orig_msg).strip()

def SRsend(conn,message):
    message+=' '*10
    conn.send(str(len(message)).encode())
    time.sleep(1)
    i=0
    f=len(message)
    print("No of frames to be sent:",f)
    wsize=int(input("Enter the sliding window size:"))
    b=""
    wsize=wsize-1
    ack=[]
    while(i!=wsize+1):
        conn.send(message[i].encode())
        ack.append(i)
        i+=1
        time.sleep(0.1)
    time.sleep(1)
    while i!=f-1:
        b=conn.recv(1024)
        b=b.decode()
        print(b)
        if(b!="ACK Lost"):
            print("ACK Received!")
            print("The sliding window range "+(str(i+1-4))+" to "+str(min(wsize+1,f-1))+"")
            print("Sending the next packet")
            ack.pop(0)
            conn.send(message[i].encode())
            ack.append(i)
            i+=1
            wsize+=1
        else:
            print("ACK of the data bit " + str(ack[0]) + " is LOST!")
            print("The sliding window remains in the range "+(str(i+1-4))+" to "+str(min(wsize+1,f-1))+"")
            print("Resending the same packet")
            conn.send(message[ack[0]].encode())
        time.sleep(0.1)
    k=1
    message = conn.recv(1024).decode()
    while(message!="Final ACK"):
        print(message)
        print("ACK Received!")
        print("The sliding window range "+(str(i+1-4))+" to "+str(min(wsize+1,f-1))+"")
        print("Sending the next packet")
        ack.pop(0)
        message = conn.recv(1024).decode()
        k+=1
    print("ACK",f-1)
    print("ACK Received!")
    print("The sliding window range "+(str(i+1-4))+" to "+str(min(wsize+1,f-1))+"")
    # print("Now sending the next packet")
    print("\nAll Packets Acknowledged")

def read_csv():
    f=open('locations.csv','r')
    ptr=0
    avail={}
    for i in f:
        if ptr!=0:
            loc,no=i.split(',')
            loc=loc.strip()
            no=int(no.strip())
            avail[loc]=no
        ptr+=1
    return avail

def write_csv(avail):
    f=open('locations.csv','w')
    f.write('locations,number of cabs\n')
    for k in avail:
        f.write(k+','+str(avail[k])+'\n')
    f.close()

def write_log(command):
    f=open('log.csv','a')
    now = datetime.datetime.now()
    f.write(now.strftime('%Y-%m-%d %H:%M:%S')+','+command+'\n')

s = socket(AF_INET, SOCK_STREAM)
port = 3000
Threadcount = 0
s.bind(('localhost', port))
s.listen(True)
print('Server listening on port 3000..')
avail=read_csv()

def multi_threaded_client(conn):
    # conn.send(str.encode('Server is working:'))
    cabs=str(avail)
    welmsg='WELCOME TO ALS CABS!!!'+'\n'+'Available Cabs:'+'\n'+cabs
    # SRsend(conn,welmsg)
    conn.send(welmsg.encode())
    while True:
        command = SRrecv(conn)
        write_log(command)
        command=command.split()
        msg=''
        skip=False
        if command[0]=='start':
            if command[1] not in avail:
                msg='Not available for asked location'
                skip=True
            if not skip and avail[command[1]]==0:
                msg='no vehicles available currently'
                skip=True
            if not skip and command[2] not in avail:
                msg='Destination is invalid'
                skip=True
            if command[1]==command[2]:
                msg='Same start and end location!!! Please change'
                skip=True
            if not skip:
                msg='Vehicle allocated'
                avail[command[1]]-=1
        elif command[0]=='end':
            if command[1] not in avail:
                skip=True
                msg='Destination is invalid'
            if not skip:
                msg='Vehicle returned'
                avail[command[1]]+=1
        elif command[0]=='bill':
            msg='Boarded at:'+command[1]+','+'Droped at:'+command[2]
            msg=msg+'\n'+'Bill amount:₹.{}'.format(math.floor((float(command[3])*22)))
            msg=msg+'\n'+'THANK YOU!! VISIT AGAIN!!'

        else:
            msg='Invalid command'

        print('vehicles available:',avail)
        SRsend(conn,msg)
        write_csv(avail)
    conn.close()

while True:
    data, address = s.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (data, ))
    Threadcount += 1
    print('Client Thread Number: ' + str(Threadcount))
s.close()
