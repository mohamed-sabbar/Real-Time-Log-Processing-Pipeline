package org.example;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;
import java.util.Collections;
import java.util.Properties;

public class consumer {

    public static void main(String[] args) {

        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "filebeat-consumer-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");


        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);


        consumer.subscribe(Collections.singletonList("test1"));


        try (var mongoClient = MongoClients.create("mongodb://localhost:27017")) {
            MongoDatabase database = mongoClient.getDatabase("logs_db");
            MongoCollection<Document> collection = database.getCollection("logs");

            while (true) {

                var records = consumer.poll(1000);


                records.forEach(record -> {
                    String message = record.value();
                    System.out.println("Consumed message from 'test1' topic: " + message);


                    Document doc = new Document("log", message);
                    collection.insertOne(doc);
                });


            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {

            consumer.close();
        }
    }
}
