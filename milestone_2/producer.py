import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

channel = connection.channel()

channel.queue_declare(queue='url_queue', durable=True)

seed_urls = [
    "https://www.wikipedia.org/",
    "https://www.youtube.com/"
]

for url in seed_urls:
    channel.basic_publish(
        exchange='',
        routing_key='url_queue',
        body=url,
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )
    print("Sent:", url)

connection.close()
