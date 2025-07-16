
from dotenv import load_dotenv
from graph import build_graph
from publisher import EventPublisher
import redis

def main():
    load_dotenv()

    graph = build_graph()
    graph.invoke({
    }, {"recursion_limit": 100})




if __name__ == "__main__":
    main()
    publisher = EventPublisher('email_notifications_channel')
    publisher.publish('Job 123 completed')  

 
