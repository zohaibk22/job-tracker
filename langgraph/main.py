
from dotenv import load_dotenv
from graph import build_graph
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    load_dotenv()

    graph = build_graph()
    graph.invoke({"status": "init"}, {"recursion_limit": 200})

if __name__ == "__main__":
    main()
 
