import socket

MAX = 5
# Create TCP/IpV4 socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Serverın aynı adresi tekrar kullanabilmesini sağlamak
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

# server
server_address = ('localhost', 3000)
print("Server Running: %s:%d" % server_address)
# Soketi ilişkilendirme bind()
sock.bind(server_address)
# Maksimum bağlantı sayısı ile dinlemeye başla
sock.listen(MAX)
# Kabul edilen bağlantı
client, address = sock.accept()

while True:
    data = client.recv(100)
    if data:
        print("Message from Client %s" % data.decode('utf-8'))
        answer = "Answer with recived message:::"+str(data.decode('utf-8'));
        client.send(answer.encode('utf-8'))
client.close()