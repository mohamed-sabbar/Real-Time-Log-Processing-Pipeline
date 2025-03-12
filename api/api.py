from flask import Flask,render_template
from flask_socketio import SocketIO
from kafka import KafkaConsumer
from collections import defaultdict
import threading
import json
app=Flask(__name__)
socketio=SocketIO(app,cors_allowed_origins="*")
kafka_config={
    "bootstrap_servers":"172.17.0.1:9092",
    "group_id":"flask-consumer",
    "auto_offset_reset":"latest"
}
last_api_stats=defaultdict(dict)
last_country_stats=defaultdict(int)
def consume_kafka_messages():
    consumer=KafkaConsumer(
        "api_stats",
        "country_stats",
        **kafka_config
    )
    for message in consumer:
        data=json.loads(message.value.decode('utf-8'))
        if message.topic=='api_stats':
            last_api_stats[data['api']]={
                "avg":data['avg'],
                "min":data['min'],
                "max":data['max']}
            socketio.emit('api_stats',data)
        elif message.topic=='country_stats':
            last_country_stats[data['country']]=data['number_of_requests']
            socketio.emit('county_stats',data)
threading.Thread(target=consume_kafka_messages,daemon=True).start()
@app.route('/')
def index():
    return render_template('index.html',api_stat=last_api_stats,api_country=last_country_stats)
if __name__=='__main__':
    socketio.run(host='0.0.0.0',port=5000,debug=True)