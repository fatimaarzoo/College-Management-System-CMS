from jose import jwt,JWTError,ExpiredSignatureError
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI,Depends,HTTPException,status
from fastapi import Request,HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.models import TokenTable
from dotenv import load_dotenv
import os

load_dotenv()
ACCESS_T0KEN_EXPIRE_MINUTES  = 30 * 24
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM  = "HS256"

def decodeJWT(jwtoken):
    print("TOKEN RECEIVED:", jwtoken)  
    try:
        payload = jwt.decode(jwtoken, SECRET_KEY , algorithms= [ALGORITHM])
        print("DECODED PAYLOAD:", payload)
        return payload
    except ExpiredSignatureError:
        # For logout, decode without verifying expiry
        payload = jwt.decode(jwtoken, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        print("Token expired but decoded for logout:", payload)
        return payload
    except JWTError as e:
        print("JWT ERROR:", e)
        return None
    
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error : bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        
    async def __call__(self, request : Request):
        credentials : HTTPAuthorizationCredentials = await super(JWTBearer,self).__call__(request)
        print("what the hell")
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403 , detail ="Invalid authentication scheme")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403 , detail ="Invalid token or expired token")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403 , detail= "Invalid authorization code")
        
    def verify_jwt(self, jwtoken : str)-> bool:
        isTokenValid : bool = False 
        
        try:
            payload = decodeJWT(jwtoken)
            print("verfied")
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
    
jwt_bearer = JWTBearer()
            
        


