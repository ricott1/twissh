import requests
import json

if __name__ == "__main__":
    x = requests.get("http://localhost:8080/gatti")
    print(x.text)
