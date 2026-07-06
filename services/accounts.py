from fastapi import APIRouter,Depends,HTTPException,Request,Response,status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from schemas import Usercreate,TokenSchema, changepassword,forgotpassword,createnewpass,requestdetails
from database.database import get_db
from database.models import User, TokenTable , SessionTable, Taskslog
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

router = APIRouter(prefix="/accounts", tags =["accounts"])
templates = Jinja2Templates(directory="templates")


load_dotenv()

ACCESS_T0KEN_EXPIRE_MINUTES  = 30 * 24 
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
MAIL_KEY = os.getenv("MAIL_TOKEN")
ALGORITHM  = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cms/accounts/login",)

pwd_context = CryptContext(
    schemes= ["pbkdf2_sha256"],
    default= "pbkdf2_sha256",
    pbkdf2_sha256__default_rounds= 30000
    
)#ARGON2 is recent

# def create_access_token(data : dict):
#     to_encode = data.copy()
#     expire    = timezone.utcnow() +timedelta(minutes=30)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def create_access_token(subject : Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_T0KEN_EXPIRE_MINUTES)
        
    to_encode   = {"exp" : expires_delta, "sub" : str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(subject : Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp" : expires_delta, "sub" : str(subject)}
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
def create_email_token(subject : Union[str,Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta =datetime.now(timezone.utc) ++ expires_delta
    else:
        expires_delta =datetime.now(timezone.utc) + timedelta(minutes=ACCESS_T0KEN_EXPIRE_MINUTES)
    to_encode   = {"exp" : expires_delta,"sub" : str(subject)}
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM )
    
def create_mail_token(user_id : int):
    payload = {
        "user_id" : user_id,
        "purpose" : "email_change",
        "exp"     : datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)


def get_current_user(token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM],options={"verify_exp": False})
    username= payload.get("sub")
    
    if username is None:
        raise HTTPException(status_code=401)
    
    return username 

def get_current_user_second(token : str ):
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM],options={"verify_exp": False})
    username= payload.get("sub")
    
    if username is None:
        raise HTTPException(status_code=401)
    
    return username 

def encrypt_password(password):
    return pwd_context.hash(password)

def check_encrypted_password(password,hashed):
    return pwd_context.verify(password,hashed)

def _purge_expired_tokens(db: Session) -> None:
    """
    Delete token rows older than 1 day.
    Extracted here so it can be called from both login and logout without
    duplicating the loop logic.
    """
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None)
    expired_ids = [
        r.user_id
        for r in db.query(TokenTable).all()
        if (cutoff - r.created_date).days > 1
    ]
    if expired_ids:
        db.query(TokenTable).filter(TokenTable.user_id.in_(expired_ids)).delete(synchronize_session=False)
        db.commit()


def register_user(username : str, mail:str, password: str,role:str, db ):
    
    if db.query(User).filter(User.username == username).first():  
        raise HTTPException(status_code=400 ,detail="Username already exists use another username")
     
    encrypted_password = encrypt_password(password)
    
    # if createuser.username and encrypted_password:# if it does not exists then not //do this instead of the current
    new_user = User(
        username = username,
        mail     = mail,
        role = role,
        password = encrypted_password
    )
    
    #if new_user : 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print("created T_T")
    return {"message":"User created!"}

# @router.post("/login", response_model= TokenSchema)   #whats here schema requestdetails?     
# def loginn(response : Response, request: Request, login_user:requestdetails, db : Session = Depends(get_db)):
#     # """
#     # httponly : a cookie parameter attribute , scripts running in the browser are not able to read its value .
#     #            this maked it harder for many XSS attacks to steal session
#     # """
#     user = db.query(User).filter(User.username == login_user.username).first() 
    
#     if user is None:
#         raise HTTPException(status_code=400 ,detail="Invalid username")
#     if not check_encrypted_password(login_user.password,user.password):
#         raise HTTPException(status_code=400 ,detail="Incorrect password")
    
#     # token = create_access_token({"sub": user.username})
#     access  = create_access_token(user.id)
#     refresh = create_refresh_token(user.id)
    
#     #token
#     token_db = TokenTable(
#         user_id = user.id,
#         access_token = access,
#         refresh_token = refresh,
#         status = True
#         )
    
#     db.add(token_db)
#     db.commit()
#     db.refresh(token_db)
    
#     #session
#     session_db = SessionTable(
#         user_id   = user.id,
#         ip_address= request.client.host,
#         device    = request.headers.get("user-agent")
        
#     )
#     db.add(session_db)
#     db.commit()
#     db.refresh(session_db)
    
#     #session .... ?Why does it store in cookie
#     request.session["username"]     = user.username
#     request.session["is_logged_in"] = True
    
#     #cookie
#     response.set_cookie(key="username", value=user.username)
#     response.set_cookie(key="access_token", value=access, httponly= True)
    
#     # return {"access_token" : token, "token_type" : "bearer" }
#     # change_password(access)
#     return { "access_token" : access , "refresh_token" : refresh}
   #whats here schema requestdetails?     
def user_login( request,response, username, password, db ):
    # """
    # httponly : a cookie parameter attribute , scripts running in the browser are not able to read its value .
    #            this maked it harder for many XSS attacks to steal session
    # """
    user = db.query(User).filter(User.username == username).first() 
    print("inside userlogin")

    if user is None:
        raise HTTPException(status_code=400 ,detail="Invalid username")
    
    print("username checkpoint passed")

    if not check_encrypted_password(password,user.password):
        raise HTTPException(status_code=400 ,detail="Incorrect password")
    
    # token = create_access_token({"sub": user.username})
    access  = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    
    #token
    token_db = TokenTable(
        user_id = user.id,
        access_token = access,
        refresh_token = refresh,
        status = True
        )
    
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    
    #session
    session_db = SessionTable(
        user_id   = user.id,
        ip_address= request.client.host,
        device    = request.headers.get("user-agent")
        
    )
    db.add(session_db)
    db.commit()
    db.refresh(session_db)
    
    #session .... ?Why does it store in cookie
    request.session["username"]     = user.username
    request.session["is_logged_in"] = True
    
    
    #cookie
    response.set_cookie(key="username", value=user.username)
    response.set_cookie(key="access_token", value=access)
    #httponly= True
    
    # return {"access_token" : token, "token_type" : "bearer" }
    # change_password(access)
    return { "access_token" : access , "refresh_token" : refresh ,"status":200 }

def protected(user = Depends(get_current_user)):
    return {"message" : f"Hello {user}"}
 
 
def getusers(dependencies = Depends(JWTBearer()),db : Session = Depends(get_db)):
    user = db.query(User).all()
    return user

def user_logout(response,request, dependencies,db):
    print("its reaching the fn")
    """
    Revoke the current access token by setting its status to False.
    Also opportunistically purges tokens older than 1 day to keep the table lean.
    """
    token = dependencies
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],options={"verify_exp": False})   # ← fix
        print("we got the payload blud",payload)
        user_id = payload.get("sub")
        print("WE got the user_id", user_id)
    except JWTError:
        print("bro throwing jwt error")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    _purge_expired_tokens(db)   # ← reusable helper instead of inline loop

    existing_token = (db.query(TokenTable).filter(TokenTable.user_id == int(user_id), TokenTable.access_token == token).first())
    
    if existing_token:
        existing_token.status = False
        active_session = db.query(SessionTable).filter(SessionTable.user_id == int(user_id),SessionTable.is_active == True).first()
        if active_session:
            active_session.is_active     = False
            active_session.last_activity = datetime.now(timezone.utc)
            
        # db.add(existing_token) adding would just be redundent
        db.commit()
        
    request.session.clear()
    
    # response.delete_cookie("access_token")
    # response.delete_cookie("username")

    return {"message": "Logged out successfully."}


def user_change_password(new_pass,confirm_pass,old_pass,db,user1):
    print(user1)
    user = db.query(User).filter(User.id == user1).first()
    print(user)
    if user is None: 
        raise HTTPException(status_code=400, detail="User not found" )
    if not check_encrypted_password(old_pass, user.password):
        raise HTTPException(status_code=400 ,detail="Invalid password")
    
    if new_pass == confirm_pass:
        send_mail(user.mail)
        notify_user(db)
        # user_id = verify_email_token(token)
        new_encrypted_password = encrypt_password(confirm_pass)
        user.password = new_encrypted_password
        db.commit()
    else:
        raise HTTPException(status_code=400 ,detail="The password doesnt match. Try Again.")
    
    return {"message": "Password changed successfully"}

def send_mail(mail,code : str | None = None):
    if code is not None:
        msg = MIMEText("Hello from Docker SMTP")
    else:
        msg = MIMEText(f"Hello from Docker SMTP. The code is {code}.")
    msg["Subject"] = "Test Email"
    msg["From"] = "test@gmail.com"
    msg["To"] = mail

    server = smtplib.SMTP("localhost", 1025)

    server.send_message(msg)

    server.quit()

    print("Email sent!")

def verify_email_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "email_change":
            raise HTTPException(status_code=400, detail="Invalid token purpose")
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


def notify_user(db:Session= Depends(get_db)):
    task = write_log_celery.delay()
    # print(task.status)#works
    # x = task.status
    # print(x)
    # print(str(task.result))#doesnt work
    # y = str(task.result)
    # print(y)
    try:
        r = Taskslog(name="Mail",task_id = str(task.id), status=task.status)
        print(r);
        db.add(r)
        db.commit()
        db.refresh(r)
        print("successfull added task to task log")
        return {"message": f"Email will be sent","task_id": task.id}
    except Exception as e:
        print(e)
        db.rollback()  

def user_create_password(user,new_pass,confirm_pass,db):
        if new_pass == confirm_pass:
            new_encrypted_password = encrypt_password(confirm_pass)
            user.password = new_encrypted_password
            db.commit()
            return("YAYA ID RETRIVED")
        else:
            raise HTTPException(status_code=400 ,detail="The password doesnt match. Try Again.")


def user_forget_password(username,mail,db):
    print("inside forget password")
    user = db.query(User).filter(User.username == username).first()
    if user is None: 
        raise HTTPException(status_code=400, detail="User not found" )
    # if(type === "send_otp"){
    # }elseif(type === "verify_otp"){
    # }
    if user.mail == mail:
        code = random.randint(1000,9999)
        # recieved_code =send_mail(mail,code)
        return code
    else:
        print("email doesnt match")
        raise HTTPException(status_code=400, detail="Mail does not match" )    

@router.get("/task-status/{task_id}")
def get_task_status(task_id:str,user = Depends(get_current_user)):
    task_result = AsyncResult(task_id,app=app) or find_task_result(task_id)
    print(str(task_result.result))
    # return {"result" : str(task_result.result)}
    if task_result.status == 'SUCCESS':
        return {"task_id":task_id,"status":"completed","result" : str(task_result.result)}#"result": task_result.result
    elif task_result.status == 'FAILURE':
        return {"task_id":task_id,"status":"failed","result" : str(task_result.result)}
    else:
        return {"task_id":task_id,"status":"in progress"}

def find_task_result(task_id:str):
    task_result = AsyncResult(task_id,app=app)
    return task_result

@router.get("/all-tasks")
def all_tasks_status(db:Session= Depends(get_db),user = Depends(get_current_user)):
    all_tasks = db.query(Taskslog).order_by(Taskslog.id.desc()).all()
    for task in all_tasks:
        if task.status != 'SUCCESS':
            # print(task.fail_flag)#to check
            if task.status == 'FAILURE':
                r = task.fail_flag
                r = r + 1 
                task.fail_flag = r
            print("old id",task.fail_flag)#to check
            #update taskslog along with failure flag  if so available
            
            print(task.task_id)
    
            task_result = find_task_result(task.task_id)
            print("new id",task_result.task_id)
            print(str(task_result.result))
            print(str(task_result.status))
            
            ###THISSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS***********************
            task.task_id = task_result.task_id
            task.status  = task_result.status
            task.result  = str(task_result.result)
            print("UPDAAATED")
            db.commit()
            db.refresh(task)

    all_tasks = db.query(Taskslog).order_by(Taskslog.id.desc()).all()
    return all_tasks

# @router.post("/retry-task")
# def retry_task(task_id:str,db:Session= Depends(get_db)):
#     task_using = db.query(Taskslog).filter(Taskslog.task_id == task_id ).first()
#     print("task_using",task_using);
#     if task_using.status == 'FAILURE':
#         print("Fail", task_id);
#         task = explicit_retry_task.delay(task_id)
#     else:
#         print("Done");
#         raise HTTPException(status_code=400 , detail="TASK IS ALREADY DONE!")
    
#     if task.status== 'SUCCESS':
#         task_using.status = task.status
#         print(str(task.result))
#         task_using.result = str(task.result)
        
#         db.commit()
#         db.refresh(task_using)
#         return {"message": "retry Successful"}
#     else:
#         raise HTTPException(status_code=400 , detail="Retry failed , try again")
    
@router.post("/retry-task")
def retry_task(task_id:str, db:Session = Depends(get_db),user = Depends(get_current_user)):

    task_using = db.query(Taskslog).filter(Taskslog.task_id == task_id).first()

    print("task_using", task_using)

    if not task_using:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_using.status != "FAILURE":
        raise HTTPException(status_code=400, detail="TASK IS ALREADY DONE!")

    retry_task_obj = write_log_celery.delay()
    
    print("task_retry",retry_task_obj.task_id)
    print(str(retry_task_obj.status))
    print(str(retry_task_obj.result))
    
    task_using.task_id = retry_task_obj.task_id
    task_using.status  = retry_task_obj.status
    task_using.result  = retry_task_obj.result
    
    db.commit()
    db.refresh(task_using)
    print("to confirm commit",task_using)

    return {
        "message": "Retry started",
        "retry_task_id": retry_task_obj.id
    }
    
# @router.post("/sendmail")
# def send_mail():
#     # Configuration
#     smtp_server = "live.smtp.mailtrap.io"
#     port = 587
#     login = "api"  # Mailtrap login
#     password = MAIL_KEY  # Mailtrap password

#     sender_email = "hello@demomailtrap.co"
#     receiver_email = "areebafatima.augurs@gmail.com"
#     reset_link = f"http://127.0.0.1:8000/docs/"
    
#     print("its reaching hearrr")

#     message = MIMEMultipart()
#     message["From"] = sender_email
#     message["To"] = receiver_email
#     message["Subject"] = html_content
    
#     html_content= f"""\
#     <html>
#     <body>
#         <h1>We received a request to change your password  </h1>
#         <p>Please Confirm by
#         "Clicking here to reset your password: {reset_link}"</p>
#     </body>
#     </html>
#     """
    

    
#     with smtplib.SMTP(smtp_server, port) as server:
#         server.starttls()
#         server.login(login, password)
#         server.sendmail(sender_email, receiver_email, message.as_string())

#     print('Sent')

# import smtplib
# from email.mime.text import MIMEText
# import secrets
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# # 1. Generate token and link
# @router.post("/sendmail")
# def send_mail():
#     token = secrets.token_urlsafe(32)
#     reset_link = f"http://127.0.0.1:8000/{token}"
#     smtp_server = "live.smtp.mailtrap.io"
#     port = 587
#     login = "api"  # Mailtrap login
#     password = MAIL_KEY  # Mailtrap password

#     sender_email = "hello@demomailtrap.co"
#     receiver_email = "areebafatima.augurs@gmail.com"

#     # 2. Compose email
#     msg = MIMEText(f"Click here to reset your password: {reset_link}")
#     msg['Subject'] = 'Password Change Request'
#     msg['From'] = 'noreply@yourdomain.com'
#     msg['To'] = 'user@example.com'

#     # 3. Send
#     with smtplib.SMTP(smtp_server, port) as server:
#         server.starttls()
#         server.login(login, password)
#         server.sendmail(sender_email, receiver_email, msg.as_string())
        
# #     print("sent")




# @router.post("/create_new_password")
# def create_new_password(request:createnewpass , db : Session=Depends(get_db)):
  
#     if not user:
#         if user is None: 
#             raise HTTPException(status_code=400, detail="User not found" )
   
  
  
  #pmst
  #mail mime
  
# from celery import Celery
# import time

# # Configure Celery to use Redis as the message broker
# celery = Celery(
#     "worker",  # This is the name of your Celery application
#     broker="redis://localhost:6379/0",  # This is the Redis connection string
#     backend="redis://localhost:6379/0",  # Optional, for storing task results
# )


# @celery.task
# def write_log_celery(message: str):
#     time.sleep(30)
#     with open("log_celery.txt", "a") as f:
#         f.write(f"{message}\n")


# from ssl import create_default_context
# from email.mime.text import MIMEText
# from smtplib import SMTP

# def send_mail2():
#     HOST=
#     USERNAME=
#     PASSWORD=
    
#     # message = MIMEText(msg.body,"html")
#     # message["From"] = USERNAME
#     # message["To"] = ",".join(msg.to)
#     # message["Subject"]= msg.subject
    
#     message = MIMEMultipart()
#     message["From"] = USERNAME
#     message["To"] = receiver_email
#     message["Subject"] = html_content
    
#     html_content= f"""\
#     <html>
#     <body>
#         <h1>We received a request to change your password  </h1>
#         <p>Please Confirm by
#         "Clicking here to reset your password: {reset_link}"</p>
#     </body>
#     </html>
#     """
    
    
#     ctx = create_default_context()
#     try:    
#         with SMTP(HOST,PORT) as server:
#             server.ehlo()
#             server.starttls(context=ctx)
#             server.ehlo()
#             server.login(USERNAME, PASSWORD)
#             server.send_message(message)
#             server.quit()
#         return {"status": 200, "errors": None}
#     except Exception as e:
#         return {"status": 500, "errors": e}
    
    
# @router.post("/send-email")
# def schedule_mail():
#     tasks.add_task(send_mail, data)
#     return {"status": 200, "message": "email has been scheduled"}
    