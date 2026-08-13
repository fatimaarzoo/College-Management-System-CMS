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
# from tasks import write_log_celery,app
from celery.result import AsyncResult
from services.accounts import *


router = APIRouter(prefix="/accounts", tags =["accounts"])
templates = Jinja2Templates(directory="templates")


@router.get("/register",response_class=HTMLResponse,include_in_schema=False)
def register_page(request: Request , db : Session = Depends(get_db)):
    message="YAY"
    return templates.TemplateResponse(request=request, name="accounts/register.html", context={})


@router.post("/register")
def register(username : str = Form(...),mail : str = Form(...),password : str = Form(...),password2 : str = Form(...),role: str = Form(...), db : Session = Depends(get_db)):
    print(username+mail+password+role)
    message = register_user(username,mail,password,role,db)
    return JSONResponse(content=message , status_code=200 )


@router.get("/login",response_class=HTMLResponse,include_in_schema=False)
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


@router.get("/change_password",response_class=HTMLResponse,include_in_schema=False)
def change_password_page(request: Request , db : Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="accounts/change_password.html", context={})

@router.post("/change_password")
def change_password(request:changepassword, db : Session= Depends(get_db),user = Depends(get_current_user)):#access:str ,
    message = user_change_password(request.new_pass,request.confirm_pass,request.old_pass,db,user)
    return JSONResponse(status_code=200 , content= {"message from backend": message, "message" :"Password Successfully changed" })

@router.get("/settings",include_in_schema=False)
def settings_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    print(token)
    if not token:
        return RedirectResponse(url="/cms/accounts/login")
    
    user_id= get_current_user_second(token)
    print(user_id) 
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    print(user ,"user role",user.role)

    return templates.TemplateResponse(request=request, name="accounts/settings.html" ,context={"user": user})#context={"user": user | None}


@router.post("/create_new_password")
def create_new_password(user,new_pass: str = Form(...),confirm_pass:str = Form(...), db : Session= Depends(get_db)):
    message=user_create_password(user,new_pass,confirm_pass,db)
    return JSONResponse(status_code=200 , content= {"message" :"User retrived the id" })


@router.get("/forget_password",response_class=HTMLResponse,include_in_schema=False)
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
      #send_mail.delay TASK
        if code == recieved_code:
            return RedirectResponse(
                    url="create_new_password/",
                    status_code=303
                )
        else: 
            return ("Code does not match")
    # return JSONResponse(status_code=200 , content= {"message" :"User retrived the id" })

    



    
