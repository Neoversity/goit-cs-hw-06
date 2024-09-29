import socket
import urllib.parse
from datetime import datetime
from pymongo import MongoClient

def start_socket_server():
    # Підключаємося до MongoDB за ім'ям сервісу в Docker
    client = MongoClient('mongo_db', 27017)
    db = client['messages_db']
    collection = db['messages']

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Слухаємо на всіх інтерфейсах (0.0.0.0) і порту 5000
        server_socket.bind(('0.0.0.0', 5000))
        server_socket.listen()
        print("Socket server listening on 0.0.0.0:5000")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                if not data:
                    break
                
                # Логуємо вхідні дані
                print(f"Raw data received: {data}")
                
                try:
                    # Розбір URL-кодованих даних
                    parsed_data = urllib.parse.parse_qs(data.decode('utf-8'))
                    print(f"Parsed data: {parsed_data}")

                    # Перевіряємо, чи заповнені всі поля
                    if 'username' in parsed_data and parsed_data['username'] and 'message' in parsed_data and parsed_data['message']:
                        # Якщо всі поля заповнені, зберігаємо повідомлення в базу
                        message_dict = {
                            'username': parsed_data['username'][0],
                            'message': parsed_data['message'][0],
                            'date': str(datetime.now())
                        }
                        collection.insert_one(message_dict)
                        print(f"Message stored in database: {message_dict}")
                        conn.sendall(b"Message received and stored")
                    else:
                        # Якщо якесь поле відсутнє або порожнє
                        print("Error: Missing 'username' or 'message'")
                        conn.sendall(b"Error: Missing 'username' or 'message'")
                except Exception as e:
                    print(f"Error occurred: {e}")
                    conn.sendall(b"Error: Could not parse data")

if __name__ == "__main__":
    start_socket_server()
