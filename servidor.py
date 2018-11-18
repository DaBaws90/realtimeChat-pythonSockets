import socket, threading, os
from datetime import datetime


class Cliente(threading.Thread):
    global clientes
    global mutex
    global logFile
    names = []

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

    def run(self):
        print("{} connected".format(self))
        # Abrimos el archivo en modo de lectura y escritura
        # with open(logFile, 'r+') as file:
        #     if file.readlines() != "":
        #         with open(logFile, 'w+') as file:
        #             file.write("'{}' connected ({})".format(self, datetime.now().strftime("%X")))
        #     else:
        #         with open(logFile, 'a+') as file:
        #             file.write("'{}' connected ({})".format(self, datetime.now().strftime("%X")))
        mutex.acquire()
        try:
            if os.path.isfile(logFile):
                if os.path.getsize(logFile) == 0:
                    with open(logFile, 'a+') as file:
                        file.write("'{}' connected ({})".format(self, datetime.now().strftime("%X")))
                else:
                    with open(logFile, 'w+') as file:
                        file.write("'{}' connected ({})".format(self, datetime.now().strftime("%X")))

            else:
                with open(logFile, 'a+') as file:
                    file.write("'{}' connected ({})".format(self, datetime.now().strftime("%X")))

        except Exception as E:
            print("Se produjo un error: {}".format(E))
        


        self.socket.send("You joined the chat room with {} ID\nType 'quit' to leave the room".format(self.id).encode())
        self.socket.send("Also, write an alias you want to use in chat room".encode())
        self.name = self.socket.recv(1024).decode()
        self.socket.send("Welcome, {}".format(self.name).encode())
        self.retransmision("joined the room")
        # for c in clientes:
        #     if self.id != c.id:
        #         c.socket.send("{} joined the room".format(self.name).encode())
        
        while True: 
            incomingMssg = self.socket.recv(1024).decode()
            if incomingMssg.lower() != "quit":
                with open(logFile, 'a+') as file:
                    # mutex.acquire()
                    file.write("Message by {} : '{}' ({})".format(self.name, incomingMssg, datetime.now().strftime("%X")))
                    file.close()

                self.retransmision("wrote: {}".format(incomingMssg))
                # for c in clientes:
                #     if self.id != c.id:
                #         c.socket.send("{} wrote: {}".format(self.name, incomingMssg).encode())
            else:
                with open(logFile, 'a+') as file:
                    file.write("'{}' has disconnected ({})".format(self.name, datetime.now().strftime("%X")))
                    file.close()

                self.socket.send("You have been successfully disconnected".encode())
                mutex.acquire()
                for c in clientes[:]:
                    if self.id == c.id:
                        clientes.remove(c)
                    else:
                        pass
                        # c.socket.send("{} has disconnected".format(self.name).encode())

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