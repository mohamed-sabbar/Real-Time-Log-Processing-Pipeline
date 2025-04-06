import { io } from "socket.io-client";

const socket = io("http://localhost:5000"); // Connexion au serveur Flask

export default socket;
