from fastapi import FastAPI
# from routers.accounts import router
from celery import Celery,shared_task
from time import sleep
# from main import send_mail
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from database.models import Taskslog

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = Celery("tasks" , broker="redis://localhost:6379", backend="redis://localhost:6379" , results_backend = 'redis://localhost:6379/0')

# app = Celery("tasks" , broker="flower://localhost:5432", backend="flower://localhost:5432" , results_backend = 'flower://localhost:5432/0')


# @app.task
# def process(x,y):
#     i=0
#     while i<5:
#         sleep(1)
#         i+=1
#         print("Processing...")
        
#     return x**2 + y**2

@app.task
def final_email():
    try:
        send_mail()
        sleep(2)
        print("EMail sent to user")
        return {"status":"sent"}
    except Exception as e:
        print(f"Attempt failed.Retrying")
        # raise self.retry(e=e , countdown=2** self.request.retries)


router= FastAPI()

def send_mail():

    msg = MIMEText("Hello Arzooooooooooooooooooooooooooooooooooooooo")
    msg["Subject"] = "Test Email"
    msg["From"] = "test@gmail.com"
    msg["To"] = "areebafatima.augurs@gmail.com"

    server = smtplib.SMTP("localhost", 1025)

    server.send_message(msg)

    server.quit()

    print("Email sent!")

router.add_middleware(SessionMiddleware,SECRET_KEY)

# @shared_task(autoretry_for(Exception,))   
@app.task(bind=True)
def write_log_celery(self):
    sleep(2)
    # with open("log_celery.txt", "a") as f:
    #     f.write(f"{message}\n")
    try:
        send_mail()
        return {"status":"sent"}
        # raise ValueError("Intentional test failure.")`                                                                               `
    except Exception as e:
        print("Attempt failed. Retrying...")
        raise self.retry(exc=e,countdown=2** self.request.retries)
        # raise Exception()
        
# @app.task(bind=True)
# def explicit_retry_task(self,task_id : str):
#     print('task_id',task_id);
#     # Source - https://stackoverflow.com/a/71746923
#     # Posted by Ajay Gupta
#     # Retrieved 2026-05-22, License - CC BY-SA 4.0
#     meta=app.backend.get_task_meta(task_id)
#     task =app.tasks['tasks.write_log_celery']
#     x = task.apply_async()
#     sleep(5)
#     print(str(x.result))
#     return {"message":"re-tried"}
        
            
# @app.task(bind=True)
# def explicit_retry_task(self, task_id: str):

#     print("task_id", task_id)

#     original_task = app.tasks['tasks.write_log_celery']

#     new_task = original_task.apply_async()

#     print("new task id", new_task.id)

#     return {
#         "message": "Task re-triggered",
#         "new_task_id": new_task.id
#     }            

    
    
    

