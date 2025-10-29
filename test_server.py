import socket
### Server side:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket
# AF_INET --> IPv4 socket
# SOCK_STREAM --> use TCP as the message transport protocol
s.bind((127.0.0.1, 8080)) # Bind HOST IP address through the given PORT
# HOST = specific IP address, the loopback address (127.0.0.1),
# or an empty string (any connection allowed)
# PORT = privileged port (e.g. 80 for HTTP) or custom port (>1023)
s.listen(n) # Listen for up to n queued connections
conn, (addr,port) = s.accept() # Accept connection (**blocking**)
data = conn.recv(N) # Receive up to N bytes from client
conn.send(data) # Send a block of data (bytes, not text)
conn.sendall(data) # Send all remaining data
conn.close() # Close the connection
### Client side:
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((HOST, PORT)) # Connect a client socket to a server
c.sendall(data) # Send all remaining data (bytes, not text)
recv_data = c.recv(bytes) # Receive data (up to given bytes)