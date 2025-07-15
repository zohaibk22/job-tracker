
from dotenv import load_dotenv
from graph import build_graph
import redis

def main():
    load_dotenv()

    graph = build_graph()
    graph.invoke({
    }, {"recursion_limit": 100})




if __name__ == "__main__":
    main()

 
