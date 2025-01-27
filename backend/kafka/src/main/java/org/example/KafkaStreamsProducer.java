package org.example;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Produced;

import java.util.Properties;

public class KafkaStreamsProducer {

    public static void main(String[] args) {

        Properties props = new Properties();
        props.put("application.id", "filebeat-to-test-topic");
        props.put("bootstrap.servers", "localhost:9092");
        props.put("default.key.serde", Serdes.String().getClass().getName());
        props.put("default.value.serde", Serdes.String().getClass().getName());
        StreamsBuilder builder = new StreamsBuilder();


        KStream<String, String> logsStream = builder.stream("logs");


        logsStream.to("test1", Produced.with(Serdes.String(), Serdes.String()));

        
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
    }
}
