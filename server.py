import socket
import threading


class Server:
    HEADER = 64
    FORMAT = 'utf-8'

    def __init__(self, ip='', port=5050, debug=False):
        if ip == '':
            self.SERVER = socket.gethostbyname(socket.gethostname())
        else:
            self.SERVER = ip
        self.PORT = port
        self.ADDR = (self.SERVER, self.PORT)
        self.DEBUG = debug
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.connections = []

    def send(self, conn, msg):
        message = msg.encode(self.FORMAT)
        msg_len = len(message)
        send_len = str(msg_len).encode(self.FORMAT)
        send_len += b' ' * (self.HEADER - len(send_len))
        conn.send(send_len)
        conn.send(message)

    def receive(self, conn, addr):
        msg_len = conn.recv(self.HEADER).decode(self.FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode(self.FORMAT)

        if self.DEBUG:
            print(f'[RECEIVED FROM {addr}] {msg}')

        return msg

    def handle_client(self, conn, addr):
        addr = f'{addr[0]}:{str(addr[1])}'
        if self.DEBUG:
            print(f'[CONNECTED] {addr}')

        try:
            username = self.receive(conn, addr)
            usernames = [conn[1] for conn in self.connections]
            if username in usernames:
                conn.close()
            self.connections.append((conn, username))
        except:
            print(f'[DISCONNECTED] {addr}')
            conn.close()
            return

        while True:
            try:
                msg = self.receive(conn, addr)
                self.broadcast(username)
                self.broadcast(msg)
            except:
                if self.DEBUG:
                    print(f'[DISCONNECTED] {addr}')
                self.connections.remove((conn, username))
                self.broadcast(username)
                self.broadcast(
                    f'opuścił właśnie serwer. Na serwerze pozostało {len(self.connections)} użytkowników.')
                conn.close()
                return

    def broadcast(self, msg):
        if self.DEBUG:
            print(f'[SENT TO ALL CLIENTS] {msg}')
        for conn, username in self.connections:
            self.send(conn, msg)

    def run(self):
        self.server.listen()
        if self.DEBUG:
            print(f'[LISTENING] {self.SERVER}')
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(
                target=self.handle_client, args=(conn, addr))
            thread.start()
            if self.DEBUG:
                print(f'[ACTIVE CONNECTIONS] {len(self.connections)}')


if __name__ == '__main__':
    print('[START]')
    server = Server(debug=True)
    server.run()
