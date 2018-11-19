import socket, threading, os
from datetime import datetime, date


class Cliente(threading.Thread):
    global clientes
    global mutex
    global logFile

    def __init__(self, soc, datos, id):
        super().__init__()
        self.socket = soc
        self.datos = datos
        self.id = id
        self.name = ""

    def __str__(self):
        return "Client '{}' with ID {}".format(self.datos, self.id)

    # Decidí iplementar esta función, ya que evitaría repetir código en el método run(), tanto para 
    # "anunciar" que alguien se unió o abandonó el chat, como para hacer broadcast de los mensajes 
    # a los demás clientes. De esta manera, el código quedaría más organizado y , de ser necesario algún cambio,
    # tan solo tendría que cambiar la lógica en esta función en lugar de en varias partes del método run().
    def retransmision(self, msg):
        for c in clientes:
            if self.id != c.id:
                c.socket.send("{} {}".format(self.name, msg).encode())

    def logging(self, msg):
        with open(logFile, 'a') as file:
            file.write("{} ({})\n".format(msg, datetime.now().strftime("%X")))

    def run(self):
        print("{} connected".format(self))
        self.logging("{} connected".format(self))

        self.socket.send("You joined the chat room with {} ID\nType 'quit' to leave the room\n\
Also, write an alias you want to use in chat room".format(self.id).encode())
        self.name = self.socket.recv(1024).decode()
        self.logging("{} is using '{}' alias".format(self, self.name))
        self.socket.send("Welcome, {}".format(self.name).encode())
        self.retransmision("joined the room")
        self.logging("{} joined the room".format(self.name))
        
        while True: 
            incomingMssg = self.socket.recv(1024).decode()
            if incomingMssg.lower() != "quit":
                self.logging("Message by {} : '{}'".format(self.name, incomingMssg))
                self.retransmision("wrote: {}".format(incomingMssg))

            else:
                self.logging("{} has disconnected".format(self.name))
                self.socket.send("You have been successfully disconnected".encode())

                mutex.acquire()
                for c in clientes[:]:
                    if self.id == c.id:
                        clientes.remove(c)
                    else:
                        pass
                # mutex.release()

                self.retransmision("has disconnected")
                mutex.release()
                self.socket.close()
                break


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 9999))
server.listen(10)

if __name__ == "__main__":
    clientes = []
    cont = 0
    logFile = "C:\\Users\\DaBaws-Laptop\\Desktop\\log.txt"
    with open(logFile, 'w') as file:
        file.write("Inicio del log: {} ({})\n\n".format(date.today(), datetime.now().strftime("%X")))

    mutex = threading.Lock()
    id = 1

    while cont < 2:
        # Chat para dos personas, pero podríamos incrementar el contador, permitiendo más usuarios simultáneos
        soc, datos = server.accept()

        c = Cliente(soc, datos, id)
        clientes.append(c)
        c.start()
        id += 1
        cont += 1

    for c in clientes:
        while c.isAlive():
            pass

    server.close()