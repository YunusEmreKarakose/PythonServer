import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# TCP/IPv4 Soketi oluştur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Set REUSEADDR (adresin tekrar kullanılabilmesi için)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#server
server_address = (IP, PORT)
# Bind server with ıp/port
server_socket.bind(server_address)
# Yeni bağlantıları dinle
server_socket.listen()

# Soket Listesi
sockets_list = [server_socket]

# Bağlı Soket Listesi
clients = {}
#client isimleri
print(f'Listening for connections on {IP}:{PORT}...')

# Mesaj alma fonksiyonu
def receive_message(client_socket):

    try:

        # Mesajı Al 
        message_header = client_socket.recv(HEADER_LENGTH)

        # Mesaj yoksa
        if not len(message_header):
            return False

        # Mesaj uzunluğu
        message_length = int(message_header.decode('utf-8').strip())

        # Mesajı obje olarak döndür
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        # Diğer durumlar için false döndür 
        return False

while True:

    #  Unix select() yada Windows select() WinSock 3 parametre ile çağır:
    #   - rlist - gelen mesajın izleneceği soketler
    #   - wlist - mesaj gönderilecek soketler
    #   - xlist - hata veren soketler
    # Returns lists:
    #   - reading - mesaj aldığımız soketler
    #   - writing - mesaj almaya uygun soketler
    #   - errors  - diğer durumdaki soketler
    # aynı zamanda soketlerin birbirini bloklamasını engeller
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Soket Listesindeki her soket için
    for notified_socket in read_sockets:

        # Yeni bağlantı kabul et
        if notified_socket == server_socket:

            # Kabul edilen bağlantı soketi ve adresi
            client_socket, client_address = server_socket.accept()

            # Client ismini al
            user = receive_message(client_socket)

            # İsim yok is client isim yollamadan kapanmıştır
            if user is False:
                continue
            #aynı adda kullanıcı olmasını engelle
            i=0
            for elem in clients.keys():
                tmp=clients[elem]
                if tmp['data']==user['data']:
                    print( "kullanıcı adı mevcut")
                else:
                    i=i+1
            #kullanıcı adı mecvut değilse kabul et
            if(i==len(clients)):
                print("yeni olustur")
                # Kabul edilen bağlantıyı  select.select() listesine ekle
                sockets_list.append(client_socket)
                # Client ismi ve başlığı
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Var olan soket 
        else:

            # Mesaj al
            message = receive_message(notified_socket)

            # Mesaj yoksa client kapandı
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                #  socket.socket() listesinden kaldır
                sockets_list.remove(notified_socket)

                # Client listesinden kaldır
                del clients[notified_socket]

                continue

            # Mesajı kimin gönderdiğini kontrol et
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            #gönderme koşulu için değişkenler
            target=""            
            tmp=message["data"].decode("utf-8").split('>')
            # eğer > ibaresi ile bir hedef gösterilmemişse tmp sadece bir string içerir
            if len(tmp)>1:
                target=tmp[0]
            # Diğer clientlara/hedef clienta alınan mesajı  yolla
            for client_socket in clients.keys():
                cltTmp=clients[client_socket]
                # Hedefe ya da herkese yaynla
                if cltTmp['data'].decode('utf-8') == target:
                    print("broadcasting to: ", cltTmp['data'].decode('utf-8'))
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                elif client_socket != notified_socket and target=="":
                   # print("broadcasting to: ", cltTmp['data'].decode('utf-8'))
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Hatalı(exepction) soketleri kaldır
    for notified_socket in exception_sockets:

        # socket.socket() listesinden kaldır
        sockets_list.remove(notified_socket)

        # clientlardna kaldır
        del clients[notified_socket]
