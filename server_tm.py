#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Modified by Tatiana Mamontova
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver

# Вне заданий: добавлены методы __init__; добавлено приветствие на сервере; не понято, что за потенциальный баг :D
# Задание 1. Аналогично спсику клиентов, создан список логинов на сервере, строки 61-71 проверяют логин.
#            Ещё был вариант создать глобальную-глобальную переменную "logins = []"
# Задание 2. Аналогично списку клиентов, создан список последних сообщений на сервере.
#            Функция send_history (строки 37-42) выдаёт старые сообщения или предлагает быть первым.
#            На строках 50-54 список с последними сообщениями пополняется и очищается от слишком старых.


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def __init__(self):
        pass

    def connectionMade(self):
        # "Потенциальный баг для внимательных =)" - это про отсутствие __init__ или про само вызывание "глобального" списка клиентов из сервера?
        self.factory.clients.append(self)
        self.sendLine("Hello there! Enter your login as \"login:<your_login>\" to start chatting.".encode())

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def send_history(self):
        if len(self.factory.last_messages) > 0:
            for i in self.factory.last_messages:
                self.sendLine(f"Old {i}".encode())
        elif len(self.factory.last_messages) == 0:
            self.sendLine("Be the first one to leave a message :)".encode())

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"

            if len(self.factory.last_messages) < 10:
                self.factory.last_messages.append(content)
            elif len(self.factory.last_messages) >= 10:
                self.factory.last_messages.append(content)
                self.factory.last_messages = self.factory.last_messages[1:]

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                self.login = content.replace("login:", "")

                if self.login not in self.factory.logins:
                    self.sendLine("Welcome!".encode())
                    self.factory.logins.append(self.login)
                    self.send_history()
                elif self.login in self.factory.logins:
                    self.sendLine(f"Login {self.login} is already taken, please try again".encode())
                    self.login = None
                    self.transport.loseConnection()

            else:
                self.sendLine("Invalid login, try again.".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    logins: list
    last_messages: list

    def __init__(self):
        self.clients = []
        self.logins = []
        self.last_messages = []

    def startFactory(self):
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
