import pika
import requests
from bs4 import BeautifulSoup
import os

MAX_PAGES = 5
pid = os.getpid()
visited = set()
page_count = 0

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='url_queue', durable=True)

channel.basic_qos(prefetch_count=1)

def callback(ch, method, properties, body):
    global page_count

    url = body.decode()

    if page_count >= MAX_PAGES:
        print("Reached maximum page limit. Stopping worker...")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        channel.stop_consuming()
        return

    if url in visited:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print("Processing:", url)

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:

            os.makedirs("pages", exist_ok=True)

            page_count += 1
            filename = f"page-{pid}-{page_count}.html"

            with open(f"pages/{filename}", "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"Saved as {filename}")

            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                new_url = link['href']
                if new_url.startswith("http") and new_url not in visited:
                    channel.basic_publish(
                        exchange='',
                        routing_key='url_queue',
                        body=new_url,
                        properties=pika.BasicProperties(
                            delivery_mode=2
                        )
                    )

            visited.add(url)

    except Exception as e:
        print("Error:", e)

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='url_queue', on_message_callback=callback)

print("Worker waiting...")
channel.start_consuming()

connection.close()

print("Worker stopped after crawling 5 pages.")
print("Total Pages Saved:", page_count)
print("Total Unique URLs Visited:", len(visited))
