from socket import *
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

    tcp_soc.send(command.encode())
    l = tcp_soc.recv(2048).decode()
    print(l)
tcp_soc.close()
