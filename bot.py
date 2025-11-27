import socket
import datetime

BOT_NAME = "bot"
VERSION = "1.0"
SERVER_HOST = "playground"
SERVER_PORT = 5000

def capture_image(image_number):
    # TODO: Replace with actual camera capture logic
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"image_{image_number}_{timestamp}.jpg"
    # Simulate image save
    with open(filename, 'w') as f:
        f.write('FAKE IMAGE DATA')
    print(f"Saved {filename}")
    return filename

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to server {SERVER_HOST}:{SERVER_PORT}...")
        s.connect((SERVER_HOST, SERVER_PORT))
        # Identify bot
        ident_msg = f"IDENTIFY {BOT_NAME} {VERSION}\n"
        s.sendall(ident_msg.encode())
        print(f"Sent identification: {ident_msg.strip()}")
        while True:
            data = s.recv(1024)
            if not data:
                print("Server closed connection.")
                break
            command = data.decode().strip()
            print(f"Received command: {command}")
            if command.startswith('TAKE_IMAGE'):
                try:
                    _, image_number = command.split()
                    capture_image(image_number)
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    main()
