from socket import *
import random
import time

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

tcp_soc = socket(AF_INET, SOCK_STREAM)
sendAddr = ('localhost', 3000)
tcp_soc.connect(sendAddr)
msg  = tcp_soc.recv(2048).decode()
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

    SRsend(tcp_soc,command)
    l = SRrecv(tcp_soc)
    print(l)
tcp_soc.close()

