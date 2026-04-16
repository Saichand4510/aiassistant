import requests
import os 
from dotenv import load_dotenv
load_dotenv()
TRELLO_API_KEY=os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN=os.getenv("TRELLO_TOKEN")
TRELLO_LIST_ID=os.getenv("TRELLO_LIST_ID")

def create_trello_task(task):
    url = "https://api.trello.com/1/cards"
    # print(task.task)
    query = {
        "name": task.task,
        "desc": f"Assignee: {task.assignee}\nDeadline: {task.deadline}",
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": TRELLO_LIST_ID
    }

    response = requests.post(url, params=query)

    # print("STATUS:", response.status_code)
    # print("TEXT:", response.text)   # 🔥 IMPORTANT

    return response.text  # temporarily

# def create_trello_task(task):
#     return {
#         "id": f"TASK-{task.id}",
#         "title": task.task,
#         "assignee": task.assignee,
#         "deadline": task.deadline,
#         "status": "created"
#     }