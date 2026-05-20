from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterSchema(BaseModel):
    name: str = Field(..., min_length=1)
    surname: str = Field(..., min_length=1)
    patronymic: Optional[str] = None
    email: EmailStr
    password: str = Field(..., min_length=6)
    password_repeat: str = Field(..., min_length=6)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    password: Optional[str] = None
    password_repeat: Optional[str] = None
    old_password: Optional[str] = None


class AccessRuleSchema(BaseModel):
    role_name: str
    element_name: str
    read_permission: bool = False
    read_all_permission: bool = False
    create_permission: bool = False
    update_permission: bool = False
    update_all_permission: bool = False
    delete_permission: bool = False
    delete_all_permission: bool = False


class AccessRuleUpdateSchema(BaseModel):
    read_permission: Optional[bool] = None
    read_all_permission: Optional[bool] = None
    create_permission: Optional[bool] = None
    update_permission: Optional[bool] = None
    update_all_permission: Optional[bool] = None
    delete_permission: Optional[bool] = None
    delete_all_permission: Optional[bool] = None


class AccessRuleResponse(BaseModel):
    id: str
    role_name: str
    element_name: str
    read_permission: bool
    read_all_permission: bool
    create_permission: bool
    update_permission: bool
    update_all_permission: bool
    delete_permission: bool
    delete_all_permission: bool

    class Config:
        from_attributes = True
