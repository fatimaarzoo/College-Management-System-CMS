from pydantic import BaseModel
from datetime import datetime

class Usercreate(BaseModel):
    
    username : str
    password : str
    
    model_config = {
        'from_attributes' : True
    }
    
class requestdetails(BaseModel):
    
    username :str
    password :str
    
    model_config = {
        'from_attributes' : True
    }
        
class TokenSchema(BaseModel):
    
    access_token  : str
    refresh_token : str
    
    model_config = {
        'from_attributes' : True
    }

# class changepassword(BaseModel):
    
#     username     :str
#     old_password :str
#     new_password :str
    
#     model_config = {
#         'from_attributes' : True
#     }
    
class TokenCreate(BaseModel):
    
    user_id       :str
    access_token  :str
    refresh_token :str
    status        :bool
    created_date  :datetime
    
    model_config = {
        'from_attributes' : True
    }
    
class changepassword(BaseModel):
    
    # username : str | None
    old_pass : str
    new_pass : str
    confirm_pass : str
    
    model_config = {
        'from_attributes' : True
    }
    
class forgotpassword(BaseModel):
    
    username : str
    mail     : str

    model_config = {
        'from_attributes' : True
    }
    
class createnewpass(BaseModel):
    

    new_pass : str
    confirm_pass : str
    
    model_config = {
        'from_attributes' : True
    }
    
