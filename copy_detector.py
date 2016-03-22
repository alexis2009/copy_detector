import os, socket, time, sys, uuid, hashlib
from threading import Thread


broadcast_port = 10500

program_key = str(uuid.uuid1())
broadcast_key = 'ba1f06d3-8847-46b2-8629-512aa7175af7'
key = 'f118eff5-454c-486c-bdb0-4ff31a0b4229'


def auth(addr, port, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)

    s.connect((addr, port))

    salt = s.recv(16)

    s.sendall(hashlib.sha256(key + salt).hexdigest())

    s.close()


class ListnerThread(Thread):

    def __inti__(self):
        Thread.__init__(self)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(None)
        s.bind(('', broadcast_port))

        while True:
            try:
                message, address = s.recvfrom(1024)

                if ':' not in message:
                    continue
                first_uuid, second_uuid, port = message.split(':')

                if second_uuid != program_key:
                    if first_uuid == broadcast_key:
                        auth(address[0], int(port))
            except (KeyboardInterrupt, SystemExit):
                raise
            except socket.timeout:
                pass


def checkCopy(timeout=0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 0))
    s.listen(1)
    s.settimeout(timeout)

    try:
        msg = broadcast_key + ':' + program_key + ':' + str(s.getsockname()[1])

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.sendto(msg, ('<broadcast>', broadcast_port))
        udp_socket.close()
    except:
        return -1

    count = 0
    while True:
        try:
            client, address = s.accept()
        except socket.timeout:
            break
        else:
            salt = os.urandom(16)

            client.send(salt)

            response = client.recv(1024)
            if response == hashlib.sha256(key + salt).hexdigest():
                count += 1

            client.close()

    s.close()

    return count


def main():
    t = ListnerThread()
    t.setDaemon(True)
    t.start()

    while True:
        # main program
        raw_input()
        print "Working copy count: {}".format(checkCopy())


if __name__ == '__main__':
    main()
