import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Виведемо шлях, який використовує сервер
        print(f"Serving from directory: {os.path.dirname(os.path.abspath(__file__))}")
        self.directory = os.path.dirname(os.path.abspath(__file__))

        # Обробка запитів на основні сторінки
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/message.html':
            self.path = '/message.html'
        elif self.path.startswith('/static/'):
            # Для статичних ресурсів
            pass
        else:
            # Якщо сторінка не знайдена, повертаємо error.html і статус 404
            self.send_error_page()
            return

        # Відправка контенту після заголовків
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/message":
            # Обробка даних форми
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            # Відправляємо отримані дані на socket-сервер
            self.send_data_to_socket(post_data)

            # Відповідь клієнту
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Message received and sent to socket server.")
        else:
            self.send_error_page()

    def send_data_to_socket(self, data):
        # Відправка даних на socket-сервер
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # sock.connect(("localhost", 5000))  # З'єднання з socket-сервером
            sock.connect(("socket_server", 5000))
            sock.sendall(data.encode("utf-8"))
            print(f"Sent data to socket server: {data}")
            response = sock.recv(1024)
            print(f"Received from socket server: {response.decode('utf-8')}")

    def send_error_page(self):
        # Відправка сторінки помилки
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # Виводимо сторінку помилки
        with open(self.directory + '/error.html', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=MyHandler, port=3000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
