from socket import *
import math
import datetime
import os
import time
import random
from _thread import *


def GBNsend(conn, message):
    conn.send(str(len(message)).encode())
    time.sleep(1)
    i = 0
    frames = len(message)
    print("No of frames to be sent:", frames)
    wsize = int(input("Enter the sliding window size:"))
    # wsize=4
    ack = ""
    wsize = wsize - 1
    k = wsize
    while i != frames:
        while (i != (frames - wsize)):
            conn.send(message[i].encode())
            ack = conn.recv(1024)
            ack = ack.decode()
            print(ack)
            if (ack != "ACK Lost"):
                print("ACK Received!")
                print("The sliding window range:" + (str(i + 1)) + " to " + str(k + 1) + "")
                print("Sending the next packet")
                i = i + 1
                k = k + 1
            else:
                print("ACK of the data bit " + (str(i)) + " is LOST!")
                print("The sliding window remains in the range " + (str(i)) + " to " + str(k) + "")
                print("Now Resending all packets from " + (str(i)) + " to " + (str(k)) + "")
            time.sleep(0.1)
        while (i != frames):
            conn.send(message[i].encode())
            ack = conn.recv(1024)
            ack = ack.decode()
            print(ack)
            if (ack != "ACK Lost"):
                print("ACK Received!")
                print("The sliding window range " + (str(i + 1)) + " to " + str(k) + "")
                if (i < frames - 1):
                    print("Sending the next packet")
                i = i + 1
            else:
                print("ACK of the data bit " + (str(i)) + " is LOST!")
                print("The sliding window remains in the range " + (str(i)) + " to " + str(k) + "")
                print("Now Resending all packets from " + (str(i)) + " to " + (str(k)) + "")
            time.sleep(0.1)


def GBNrecv(connection):
    k = connection.recv(2048).decode()
    k = int(k)
    i = 0
    originalmsg = ''
    ack = ''
    f = random.randint(0, 1)
    nxtchr = ''
    while i != k:
        f = abs(random.randint(0, 1) - random.randint(0, 1))
        if (f == 0):
            ack = 'ACK ' + str(i)
            nxtchr = connection.recv(1024)
            nxtchr = nxtchr.decode()
            connection.send(ack.encode())
            originalmsg = originalmsg + nxtchr
            i = i + 1
        else:
            ack = 'ACK Lost'
            nxtchr = connection.recv(1024)
            nxtchr = nxtchr.decode()
            connection.send(ack.encode())
    # print('The message received is :', originalmsg)
    return originalmsg


def read_csv():
    f = open('locations.csv', 'r')
    ptr = 0
    avail = {}
    for i in f:
        if ptr != 0:
            loc, no = i.split(',')
            loc = loc.strip()
            no = int(no.strip())
            avail[loc] = no
        ptr += 1
    return avail


def write_csv(avail):
    f = open('locations.csv', 'w')
    f.write('locations,number of cabs\n')
    for k in avail:
        f.write(k + ',' + str(avail[k]) + '\n')
    f.close()


def write_log(command):
    f = open('log.csv', 'a')
    now = datetime.datetime.now()
    f.write(now.strftime('%Y-%m-%d %H:%M:%S') + ',' + command + '\n')


s = socket(AF_INET, SOCK_STREAM)
port = 3000
Threadcount = 0
s.bind(('localhost', port))
s.listen(True)
print('Server listening on port 3000..')
avail = read_csv()


def multi_threaded_client(conn):
    cabs = str(avail)
    welmsg = 'WELCOME TO ALS CABS!!!' + '\n' + 'Available Cabs:' + '\n' + cabs
    conn.send(welmsg.encode())
    # GBNsend(conn,welmsg)  
    while True:
        command = GBNrecv(conn)
        write_log(command)
        command = command.split()
        msg = ''
        skip = False
        if command[0] == 'start':
            if command[1] not in avail:
                msg = 'Not available for asked location'
                skip = True
            if not skip and avail[command[1]] == 0:
                msg = 'no vehicles available currently'
                skip = True
            if not skip and command[2] not in avail:
                msg = 'Destination is invalid'
                skip = True
            if command[1] == command[2]:
                msg = 'Same start and end location!!! Please change'
                skip = True
            if not skip:
                msg = 'Vehicle allocated'
                avail[command[1]] -= 1
        elif command[0] == 'end':
            if command[1] not in avail:
                skip = True
                msg = 'Destination is invalid'
            if not skip:
                msg = 'Vehicle returned'
                avail[command[1]] += 1
        elif command[0] == 'bill':
            msg = 'Boarded at:' + command[1] + ',' + 'Droped at:' + command[2]
            msg = msg + '\n' + 'Bill amount:₹.{}'.format(math.floor((float(command[3]) * 22)))
            msg = msg + '\n' + 'THANK YOU!! VISIT AGAIN!!'

        else:
            msg = 'Invalid command'

        print('vehicles available:', avail)
        # conn.send(msg.encode())
        GBNsend(conn, msg)
        write_csv(avail)

        # if not command:
        #     break
        # conn.sendall(str.encode(response))
    conn.close()


while True:
    data, address = s.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (data,))
    Threadcount += 1
    print('Client Thread Number: ' + str(Threadcount))
s.close()