
from dotenv import load_dotenv
from graph import build_graph

def main():
    load_dotenv()

    graph = build_graph()
    graph.invoke({
    }, {"recursion_limit": 200})

if __name__ == "__main__":
    main()
 
