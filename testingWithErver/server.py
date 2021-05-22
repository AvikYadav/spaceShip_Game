import socket
import threading
import time
clients =[]
power=[]
server = socket.socket()
host='localhost'
port=8888
server.bind((host,port))
server.listen(5)
def accept():
    while True:
        conn,addr= server.accept()
        clients.append(conn)
        print(clients)
        print(f'client connection {addr}')
        print(len(clients))

        print(clients)
        print('this is vlient i')
            # i.send('!READY!'.encode('utf-8'))
        print('sended')
        msg2 = conn.recv(4026).decode('utf-8')
        print(msg2)
        power.append(msg2)
        if len(power) < 2:
            continue
        powerup()
        if len(clients) < 2:
            continue
        for i in clients:
            i.send('!READY!'.encode('utf-8'))
            thread = threading.Thread(target=recieve, args=(i,))
                # thread.daemon = True
            thread.start()



def recieve(client):
    print('thread working',client)
    while True:
        recoieve = client.recv(4026).decode('utf')
        send_coordinate(recoieve,client)
def send_coordinate(coordinates,coonn):
    try:
        ind = clients.index(coonn)
        ind-=1
        print(coordinates)
        x,y,mortarAngle,shoot,health = coordinates.split(',')
        print(x,y)
        connection = clients[ind]
        connection.send(f'{x},{y},{mortarAngle},{shoot},{health}'.encode('utf-8'))
    except Exception as err:
        print(err)
        pass
def powerup():
    m1=power[0]
    m2=power[1]
    print(m1,m2)
    j = clients[0]
    j1 = clients[1]
    ind = clients.index(j)
    ind -= 1
    connection = clients[ind]
    ind2 = clients.index(j1)
    ind2 -= 1
    connection2 = clients[ind2]
    connection.send(m1.encode('utf-8'))
    connection2.send(m2.encode('utf-8'))
def send_laser_info(message,coon):
    ind = clients.index(coon)
    ind -= 1
    connection = clients[ind]
    connection.send(message.encode('utf-8'))
accept()