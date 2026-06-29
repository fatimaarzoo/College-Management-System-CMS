from fastapi import APIRouter,Depends,HTTPException,Request,Response,status,Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from schemas import Usercreate,TokenSchema, changepassword,forgotpassword,createnewpass,requestdetails
from database.database import get_db
from database.models import User, TokenTable , SessionTable, Taskslog, Student, Teacher
from jose import jwt,JWTError
from typing import Union, Any
from datetime import datetime,timedelta,timezone
from dotenv import load_dotenv
import os
from core.auth_bearer import JWTBearer
import mailtrap as mt
from typing import Dict
import smtplib
import random
from starlette.middleware.sessions import SessionMiddleware
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tasks import write_log_celery,app
from celery.result import AsyncResult
from services.accounts import *


router = APIRouter(prefix="/accounts", tags =["accounts"])
templates = Jinja2Templates(directory="templates")


@router.get("/register",response_class=HTMLResponse)
def register_page(request: Request , db : Session = Depends(get_db)):
    message="YAY"
    return templates.TemplateResponse(request=request, name="accounts/register.html", context={})


@router.post("/register")
def register(username : str = Form(...),mail : str = Form(...),password : str = Form(...),password2 : str = Form(...),role: str = Form(...), db : Session = Depends(get_db)):
    print(username+mail+password+role)
    message = register_user(username,mail,password,role,db)#send role???
    return JSONResponse(content=message , status_code=200 )

@router.get("/login",response_class=HTMLResponse)
def login_page(request: Request , db : Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="accounts/login.html", context={})
 
@router.post("/login")     
def login(data:requestdetails,request: Request,response:Response, db : Session = Depends(get_db)):
    print("username"+data.username+ "password"+data.password)
    message= user_login(request,response,data.username,data.password,db)
    return message


@router.get("/protected")
def protected(user = Depends(get_current_user)):
    return {"message" : f"Hello {user}"}
 
@router.get("/getusers")    
def getusers(dependencies = Depends(JWTBearer()),db : Session = Depends(get_db)):
    user = db.query(User).all()
    return user

@router.post("/logout")
def logout(response:Response,request : Request, token:str = Depends(JWTBearer(auto_error=False)),db: Session = Depends(get_db)):
    print("its inside the first fn")
    message = user_logout(response,request,token,db)
    # if token:
    # # blacklist token in DB regardless of expiry
    #     db.add(TokenTable(access_token=token, status=False))
    #     db.commit()
    print(message)
    return {"message": message, }

@router.get("/change_password",response_class=HTMLResponse)
def change_password_page(request: Request , db : Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="accounts/change_password.html", context={})

@router.post("/change_password")
def change_password(request:changepassword, db : Session= Depends(get_db),user = Depends(get_current_user)):#access:str ,
    message = user_change_password(request.new_pass,request.confirm_pass,request.old_pass,db,user)
    return JSONResponse(status_code=200 , content= {"message from backend": message, "message" :"Password Successfully changed" })

@router.get("/settings")
def settings_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    print(token)
    if not token:
        return RedirectResponse(url="/cms/accounts/login")
    
    user_id= get_current_user_second(token)
    print(user_id) 
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    print(user ,"user role",user.role)
    # if user.role == "student":
    #     profile = db.query(Student).filter(Student.user_id == user.id).first()
    #     print("Profile",profile)
    # elif user.role == "teacher":
    #     profile = db.query(Teacher).filter(Teacher.user_id == user.id).first()
    #     print("Profile",profile)
    # else:
    #     profile = "guest" 
    #     print("Profile",profile)
    #u are not aassigning any user_id to the anywhere ask abt that
    return templates.TemplateResponse(request=request, name="accounts/settings.html" ,context={"user": user})#context={"user": user | None}

# @router.get("/settings")
# def settings_page(request : Request):
#     return templates.TemplateResponse(request=request, name="accounts/settings.html", context={})

# @router.get('/get_user')
# def get_user(user1 = Depends(get_current_user),db : Session= Depends(get_db)):
#     print(user1)
    # user = db.query(User).filter(User.username == user1).first()
    # print(user.username, user.id,user.mail,user.role)
    # return user

@router.post("/create_new_password")
def create_new_password(user,new_pass: str = Form(...),confirm_pass:str = Form(...), db : Session= Depends(get_db)):
    message=user_create_password(user,new_pass,confirm_pass,db)
    return JSONResponse(status_code=200 , content= {"message" :"User retrived the id" })


@router.get("/forget_password",response_class=HTMLResponse)
def forget_password_page(request : Request):
    return templates.TemplateResponse(request=request, name="accounts/forget_password.html", context={})

@router.post("/forget_password")
def forget_password(username: str = Form(...),mail:str = Form(...), db : Session= Depends(get_db)):
    print(username+mail)
    user = db.query(User).filter(User.username == username).first()
    if user is None: 
        raise HTTPException(status_code=400, detail="User not found" )
    else:
        code = user_forget_password(username,mail,db)
        print(code)
        recieved_code = int(input("Enter the code: "))
        if code == recieved_code:
            return RedirectResponse(
                    url="create_new_password/",
                    status_code=303
                )
        else: 
            return ("Code does not match")
    return JSONResponse(status_code=200 , content= {"message" :"User retrived the id" })

    


# @router.post("/notify")
# def notify_user(db:Session= Depends(get_db),user = Depends(get_current_user)):
#     task = write_log_celery.delay()
#     # print(task.status)#works
#     # x = task.status
#     # print(x)
#     # print(str(task.result))#doesnt work
#     # y = str(task.result)
#     # print(y)
#     try:
#         r = Taskslog(name="Mail",task_id = str(task.id), status=task.status)
#         print(r);
#         db.add(r)
#         db.commit()
#         db.refresh(r)
#         print("successfull added task to task log")
#         return {"message": f"Email will be sent","task_id": task.id}
#     except Exception as e:
#         print(e)
#         db.rollback()  
    

# @router.get("/task-status/{task_id}")
# def get_task_status(task_id:str,user = Depends(get_current_user)):
#     task_result = AsyncResult(task_id,app=app) or find_task_result(task_id)
#     print(str(task_result.result))
#     # return {"result" : str(task_result.result)}
#     if task_result.status == 'SUCCESS':
#         return {"task_id":task_id,"status":"completed","result" : str(task_result.result)}#"result": task_result.result
#     elif task_result.status == 'FAILURE':
#         return {"task_id":task_id,"status":"failed","result" : str(task_result.result)}
#     else:
#         return {"task_id":task_id,"status":"in progress"}

# def find_task_result(task_id:str):
#     task_result = AsyncResult(task_id,app=app)
#     return task_result

# @router.get("/all-tasks")
# def all_tasks_status(db:Session= Depends(get_db),user = Depends(get_current_user)):
#     all_tasks = db.query(Taskslog).order_by(Taskslog.id.desc()).all()
#     for task in all_tasks:
#         if task.status != 'SUCCESS':
#             # print(task.fail_flag)#to check
#             if task.status == 'FAILURE':
#                 r = task.fail_flag
#                 r = r + 1 
#                 task.fail_flag = r
#             print("old id",task.fail_flag)#to check
#             #update taskslog along with failure flag  if so available
            
#             print(task.task_id)
    
#             task_result = find_task_result(task.task_id)
#             print("new id",task_result.task_id)
#             print(str(task_result.result))
#             print(str(task_result.status))
            
#             ###THISSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS***********************
#             task.task_id = task_result.task_id
#             task.status  = task_result.status
#             task.result  = str(task_result.result)
#             print("UPDAAATED")
#             db.commit()
#             db.refresh(task)

#     all_tasks = db.query(Taskslog).order_by(Taskslog.id.desc()).all()
#     return all_tasks

# # @router.post("/retry-task")
# # def retry_task(task_id:str,db:Session= Depends(get_db)):
# #     task_using = db.query(Taskslog).filter(Taskslog.task_id == task_id ).first()
# #     print("task_using",task_using);
# #     if task_using.status == 'FAILURE':
# #         print("Fail", task_id);
# #         task = explicit_retry_task.delay(task_id)
# #     else:
# #         print("Done");
# #         raise HTTPException(status_code=400 , detail="TASK IS ALREADY DONE!")
    
# #     if task.status== 'SUCCESS':
# #         task_using.status = task.status
# #         print(str(task.result))
# #         task_using.result = str(task.result)
        
# #         db.commit()
# #         db.refresh(task_using)
# #         return {"message": "retry Successful"}
# #     else:
# #         raise HTTPException(status_code=400 , detail="Retry failed , try again")
    
# @router.post("/retry-task")
# def retry_task(task_id:str, db:Session = Depends(get_db),user = Depends(get_current_user)):

#     task_using = db.query(Taskslog).filter(Taskslog.task_id == task_id).first()

#     print("task_using", task_using)

#     if not task_using:
#         raise HTTPException(status_code=404, detail="Task not found")

#     if task_using.status != "FAILURE":
#         raise HTTPException(status_code=400, detail="TASK IS ALREADY DONE!")

#     retry_task_obj = write_log_celery.delay()
    
#     print("task_retry",retry_task_obj.task_id)
#     print(str(retry_task_obj.status))
#     print(str(retry_task_obj.result))
    
#     task_using.task_id = retry_task_obj.task_id
#     task_using.status  = retry_task_obj.status
#     task_using.result  = retry_task_obj.result
    
#     db.commit()
#     db.refresh(task_using)
#     print("to confirm commit",task_using)

#     return {
#         "message": "Retry started",
#         "retry_task_id": retry_task_obj.id
#     }
    
# # @router.post("/send-mail")



# # @router.post("/sendmail")
# # def send_mail():
# #     # Configuration
# #     smtp_server = "live.smtp.mailtrap.io"
# #     port = 587
# #     login = "api"  # Mailtrap login
# #     password = MAIL_KEY  # Mailtrap password

# #     sender_email = "hello@demomailtrap.co"
# #     receiver_email = "areebafatima.augurs@gmail.com"
# #     reset_link = f"http://127.0.0.1:8000/docs/"
    
# #     print("its reaching hearrr")

# #     message = MIMEMultipart()
# #     message["From"] = sender_email
# #     message["To"] = receiver_email
# #     message["Subject"] = html_content
    
# #     html_content= f"""\
# #     <html>
# #     <body>
# #         <h1>We received a request to change your password  </h1>
# #         <p>Please Confirm by
# #         "Clicking here to reset your password: {reset_link}"</p>
# #     </body>
# #     </html>
# #     """
    

    
# #     with smtplib.SMTP(smtp_server, port) as server:
# #         server.starttls()
# #         server.login(login, password)
# #         server.sendmail(sender_email, receiver_email, message.as_string())

# #     print('Sent')

        






   
  
  
#   #pmst
#   #mail mime
  
# # from celery import Celery
# # import time

# # # Configure Celery to use Redis as the message broker
# # celery = Celery(
# #     "worker",  # This is the name of your Celery application
# #     broker="redis://localhost:6379/0",  # This is the Redis connection string
# #     backend="redis://localhost:6379/0",  # Optional, for storing task results
# # )


# # @celery.task
# # def write_log_celery(message: str):
# #     time.sleep(30)
# #     with open("log_celery.txt", "a") as f:
# #         f.write(f"{message}\n")


# # from ssl import create_default_context
# # from email.mime.text import MIMEText
# # from smtplib import SMTP

# # def send_mail2():
# #     HOST=
# #     USERNAME=
# #     PASSWORD=
    
# #     # message = MIMEText(msg.body,"html")
# #     # message["From"] = USERNAME
# #     # message["To"] = ",".join(msg.to)
# #     # message["Subject"]= msg.subject
    
# #     message = MIMEMultipart()
# #     message["From"] = USERNAME
# #     message["To"] = receiver_email
# #     message["Subject"] = html_content
    
# #     html_content= f"""\
# #     <html>
# #     <body>
# #         <h1>We received a request to change your password  </h1>
# #         <p>Please Confirm by
# #         "Clicking here to reset your password: {reset_link}"</p>
# #     </body>
# #     </html>
# #     """
    
    
# #     ctx = create_default_context()
# #     try:    
# #         with SMTP(HOST,PORT) as server:
# #             server.ehlo()
# #             server.starttls(context=ctx)
# #             server.ehlo()
# #             server.login(USERNAME, PASSWORD)
# #             server.send_message(message)
# #             server.quit()
# #         return {"status": 200, "errors": None}
# #     except Exception as e:
# #         return {"status": 500, "errors": e}
    
    
# # @router.post("/send-email")
# # def schedule_mail():
# #     tasks.add_task(send_mail, data)
# #     return {"status": 200, "message": "email has been scheduled"}
    