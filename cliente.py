import socket, sys, select, datetime

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("localhost", 9999))
    print("Successfuly connected")
except:
    print("Unable to connect")
    sys.exit()

# Esta función nos permite poner una cabecera a cada mensaje minetras enviamos o recibimos, indistintamente de la operación.
# 
def header():
    sys.stdout.write(">> ")
    sys.stdout.flush()

while True:
    # Comprobamos si se cerró la conexion para salir del while True antes de llamar a la función select, o nos arrojaría
    # un error al tratar de usar dicha conexion (s), puesto que no estaría disponible
    if s._closed:
        break

    possibilities = select.select([s], [], [], 1)[0]
    import msvcrt
    if msvcrt.kbhit(): possibilities.append(sys.stdin)
    # Nos permite "escuchar" hasta que haya un evento de lectura disponible, ya sea un mensaje del servidor, 
    # o que el usuario introduzca un mensaje. Esta función es completamente funcional en Unix, pero en Windows,
    # haciendo uso de WinSock, tenemos que hacer un apaño para que funcione, que consiste en importar el modulo
    # msvcrt y hacer un append de sys.stdin, ya que winSock solo reconoce elementos que sea sockets con la funcion
    # select(), así que tuve que buscar la manera de poder hacerlo en windows y este es el resultado. Básicamente
    # le damos una lista con las posibilidades que existen, o bien un mensaje del serivdor, o del usuario, y escucha dinamicamente
    # hasta que uno de los dos requiera interactuar. De esa manera, nuestro script no se verá encasillado en esperar para mandar
    # o para escribir, si no que recibirá cuando pueda, y escribirá cuando quiera
    
    for p in possibilities:
        # Por cada una de esas posibilidades, que compurebe cual está "activa" en cada momento. Si es un mensaje entrante,
        # lo imprime, y si el usario escribe un mensaje, lo manda.
        if p != s:
            message = input()
            if message.lower() == 'quit':
                s.send("quit".encode())
                print(s.recv(1024).decode())
                s.close()
            else:
                s.send(message.encode())
                header()
            
        else:

            incoming = p.recv(1024).decode()
            if not incoming:
                s.send("quit".encode())
                s.close()
            else:
                print("{} ({})".format(incoming, datetime.datetime.now().strftime("%X")))
                header()