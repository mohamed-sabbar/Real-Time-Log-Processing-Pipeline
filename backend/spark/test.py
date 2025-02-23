
import socket
# Créer un serveur socket
host = 'localhost'
port = 9999
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print(f"En attente de connexions sur {host}:{port}...")
client_socket, client_address = server_socket.accept()
print(f"Connexion acceptée de {client_address}")

# Fonction pour envoyer des messages via le socket
def send_message_to_socket(message):
    client_socket.send(message.encode())

# Ne ferme pas la connexion et attends des messages
while True:
    try:
        # Attendre et recevoir des messages
        message = client_socket.recv(1024).decode()
        print("Message reçu:", message)
    except Exception as e:
        print(f"Erreur: {e}")
        break
