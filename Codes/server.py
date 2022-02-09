 from socket import *
import math
import datetime
import os
from _thread import *

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
print('Listening on port 3000..')
avail=read_csv()
 
def multi_threaded_client(conn):
    # conn.send(str.encode('Server is working:'))
    cabs=str(avail)
    welmsg='WELCOME TO ALS CABS!!!'+'\n'+'Available Cabs:'+'\n'+cabs
    conn.send(welmsg.encode())   
    while True:
        command = conn.recv(2048).decode()
        # response = 'Server message: '+command
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
        conn.send(msg.encode())
        write_csv(avail) 
        
        # if not command:
        #     break
        # conn.sendall(str.encode(response))
    conn.close() 

while True:
    data, address = s.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (data, ))
    Threadcount += 1
    print('Thread Number: ' + str(Threadcount))
s.close()
