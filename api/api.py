from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from kafka import KafkaConsumer, errors as kafka_errors
import threading
import random
import time
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app,
                   cors_allowed_origins="*",
                  async_mode='threading')


KAFKA_CONFIG = {
    "bootstrap_servers": "localhost:9093",
    "group_id": "flask-dashboard",
    "auto_offset_reset": "latest",
    "value_deserializer": lambda v: json.loads(v.decode('utf-8'))
}


def generate_random_data():
    endpoints = [
        "GET /api/users",
        "POST /api/login",
        "DELETE /api/users",
        "PUT /api/products",
        "GET /api/orders"
    ]
    
    countries = ["US", "FR", "DE", "GB", "JP", "CA", "AU", "BR"]
    
    return {
        "api_stats": {
            endpoint: {
                "avg": random.uniform(50, 500),
                "min": random.uniform(50, 200),
                "max": random.uniform(200, 1000)
            } for endpoint in endpoints
        },
        "country_stats": {
            country: random.randint(100, 2000) for country in countries
        }
    }

current_data = generate_random_data()

def update_random_data():
    
    global current_data
    
    while True:
        # Mise à jour des stats API
        for endpoint in current_data["api_stats"]:
            current_data["api_stats"][endpoint] = {
                "avg": max(10, current_data["api_stats"][endpoint]["avg"] + random.uniform(-20, 20)),
                "min": max(10, current_data["api_stats"][endpoint]["min"] + random.uniform(-10, 10)),
                "max": max(50, current_data["api_stats"][endpoint]["max"] + random.uniform(-30, 30))
            }
            socketio.emit("api_update", {
                "endpoint": endpoint,
                "stats": current_data["api_stats"][endpoint]
            })
        
        # Mise à jour des stats pays
        for country in current_data["country_stats"]:
            change = random.randint(-50, 100)
            current_data["country_stats"][country] = max(0, current_data["country_stats"][country] + change)
            socketio.emit("country_update", {
                "country": country,
                "count": current_data["country_stats"][country]
            })
        
        time.sleep(2)  # Intervalle entre les mises à jour

def consume_kafka_messages():
    try:
        consumer = KafkaConsumer(
            "api_stats",
            "country_stats",
            **KAFKA_CONFIG
        )
        print("✅ Connecté à Kafka - Mode temps réel activé")
        
        for message in consumer:
            try:
                data = message.value
                
                if message.topic == "api_stats":
                    socketio.emit("api_update", {
                        "endpoint": data["api"],
                        "stats": {
                            "avg": round(float(data["avg"]), 2),
                            "min": int(data["min"]),
                            "max": int(data["max"])
                        }
                    })
                    
                elif message.topic == "country_stats":
                    socketio.emit("country_update", {
                        "country": data["country"].upper(),
                        "count": int(data["number_of_requests"])
                    })
                    
            except Exception as e:
                print(f"❌ Erreur traitement message Kafka: {str(e)}")
                
    except kafka_errors.NoBrokersAvailable:
        print("⚠️ Kafka indisponible - Activation du mode aléatoire")
        update_random_data()
    except Exception as e:
        print(f"⚠️ Erreur Kafka: {str(e)} - Activation du mode aléatoire")
        update_random_data()

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "mode": "kafka" if is_kafka_available() else "random"
    })

@app.route('/api/data')
def get_all_data():
    return jsonify(current_data)

def is_kafka_available():
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
            consumer_timeout_ms=2000
        )
        consumer.topics()
        return True
    except:
        return False

if __name__ == '__main__':
    if is_kafka_available():
        kafka_thread = threading.Thread(target=consume_kafka_messages, daemon=True)
    else:
        print("🔍 Kafka non disponible - Lancement du générateur aléatoire")
        kafka_thread = threading.Thread(target=update_random_data, daemon=True)
    
    kafka_thread.start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)  