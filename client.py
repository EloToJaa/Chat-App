from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog
import threading
import socket


class Client:
    HEADER = 64
    FORMAT = 'utf-8'

    def __init__(self, server, username, port=5050, debug=False):
        self.SERVER = server
        self.PORT = port
        self.ADDR = (self.SERVER, self.PORT)
        self.DEBUG = debug
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.username = username
        self.run = True
        if self.DEBUG:
            print('[START]')

    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_len = len(message)
        send_len = str(msg_len).encode(self.FORMAT)
        send_len += b' ' * (self.HEADER - len(send_len))
        self.client.send(send_len)
        self.client.send(message)
        if self.DEBUG:
            print(f'[SENT] {msg}')

    def receive(self):
        msg_len = self.client.recv(self.HEADER).decode(self.FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = self.client.recv(msg_len).decode(self.FORMAT)
            if self.DEBUG:
                print(f'[RECEIVED] {msg}')
        return msg

    def listening(self, gui=None):
        if self.DEBUG:
            print(f'[CONNECTED] {self.SERVER}')

        self.send(self.username)

        while self.run:
            try:
                username = self.receive()
                msg = self.receive()
                gui.receive_msg(username, msg)
            except:
                print(f'[DISCONNECTED] {self.SEVER}')
                self.client.close()
                return


class Ui_MainWindow(object):
    WIDTH, HEIGHT = 645, 440
    FONT_NAME = 'Arial'
    FONT_SIZE = 13
    FONT_BOLD = 75

    def setupUi(self, MainWindow):
        MainWindow.setObjectName('MainWindow')
        MainWindow.setFixedSize(self.WIDTH, self.HEIGHT)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')

        # message input
        self.msg_input = QtWidgets.QLineEdit(self.centralwidget)
        self.msg_input.setGeometry(QtCore.QRect(10, 390, 541, 41))
        font = QtGui.QFont()
        font.setFamily(self.FONT_NAME)
        font.setPointSize(self.FONT_SIZE)
        self.msg_input.setFont(font)
        self.msg_input.setObjectName('msg_input')
        self.msg_input.returnPressed.connect(self.send_msg)

        # send button
        self.msg_send = QtWidgets.QPushButton(self.centralwidget)
        self.msg_send.setGeometry(QtCore.QRect(554, 390, 81, 41))
        font = QtGui.QFont()
        font.setFamily(self.FONT_NAME)
        font.setPointSize(self.FONT_SIZE)
        font.setBold(True)
        font.setWeight(self.FONT_BOLD)
        self.msg_send.setFont(font)
        self.msg_send.setObjectName('msg_send')
        self.msg_send.clicked.connect(self.send_msg)

        # chat text
        self.chat_text = QtWidgets.QTextEdit(self.centralwidget)
        self.chat_text.setGeometry(QtCore.QRect(10, 33, 625, 350))
        font = QtGui.QFont()
        font.setFamily(self.FONT_NAME)
        font.setPointSize(self.FONT_SIZE)
        self.chat_text.setFont(font)
        self.chat_text.setObjectName('chat_text')
        self.chat_text.setReadOnly(True)

        # info text
        self.info_label = QtWidgets.QLabel(self.centralwidget)
        self.info_label.setGeometry(QtCore.QRect(16, 0, 621, 31))
        font = QtGui.QFont()
        font.setFamily(self.FONT_NAME)
        font.setPointSize(self.FONT_SIZE)
        font.setBold(True)
        font.setWeight(self.FONT_BOLD)
        self.info_label.setFont(font)
        self.info_label.setObjectName('info_label')

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.ip_input()
        self.username_input()

        self.client = Client(self.server, self.username)
        receive_thread = threading.Thread(
            target=self.client.listening, args=(self,))
        receive_thread.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('MainWindow', 'Chat App'))
        self.msg_send.setText(_translate('MainWindow', 'Send'))
        self.info_label.setText(_translate('MainWindow', 'Nazwa użytkownika:'))

    def receive_msg(self, username, msg):
        if username == self.username:
            message = f'<b style="color: blue">{username}:</b> {msg}'
        else:
            message = f'<b>{username}:</b> {msg}'

        self.chat_text.append(message)
        self.chat_text.moveCursor(QtGui.QTextCursor.End)

    def send_msg(self):
        msg = self.msg_input.text()
        self.msg_input.setText('')
        if msg != '':
            self.client.send(msg)

    def ip_input(self):
        self.server, ok = QInputDialog.getText(
            MainWindow, 'Serwer IP', 'Podaj adres IP serwera:')
        if self.server in ['localhost', '127.0.0.1']:
            self.server = socket.gethostbyname(socket.gethostname())
        if not ok or self.server == '':
            self.client.run = False
            sys.exit(app.exec_())

    def username_input(self):
        self.username, ok = QInputDialog.getText(
            MainWindow, 'Username', 'Podaj nazwe użytkownika:')
        if not ok or self.username == '':
            self.client.run = False
            sys.exit(app.exec_())
        self.info_label.setText(f'Nazwa użytkownika: {self.username}')


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
