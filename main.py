from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker, session


from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, EmailStr

app = FastAPI(description="Welcome to Fastapi build a web api response and request HTTP server.")

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
  __tablename__ = "users"
  
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)
  email = Column(String, unique=True, index=True)
  
Base.metadata.create_all(bind=engine)

def get_db():
  db = sessionLocal()
  try: 
    yield db
  finally: 
    db.close()
    
class UserCreate(BaseModel):
  name: str
  email: EmailStr
  
class UserResponse(BaseModel):
  id: int
  name: str
  email: EmailStr
  
  class Config:
    orm_mode = True
    
    
@app.post("/users/", response_model=UserResponse, description="Create user end point")
async def create_user(user: UserCreate, db: session = Depends(get_db)):
  db_user = User(name=user.name, email=user.email) 
  db.add(db_user)
  db.commit()
  db.refresh(db_user) 
  return db_user


@app.get("/users/", response_model=List[UserResponse], description="Get response list of users")
async def read_users(skips:int=0, limit:int=10, db: session = Depends(get_db)):
  users = db.query(User).offset(skips).limit(limit).all()
  return users

@app.get("/users/{user_id}", response_model=UserResponse, description="Get response user")
async def read_user(user_id: int, db: session = Depends(get_db)):
  user = db.query(User).filter(User.id == user_id).first()
  
  if user is None:
    raise HTTPException(
      status_code=404,
      detail="user not founded"
    )
  return user

class UserUpdate(BaseModel):
  name: Optional[str] = None
  email: Optional[EmailStr] = None
  
  
@app.put("/users/{user_id}", response_model=UserResponse, description="Update user data")
async def update_user(user_id: int,user: UserUpdate, db: session = Depends(get_db)):
  db_user = db.query(User).filter(User.id == user_id).first()
  
  if db_user is None: 
    raise HTTPException(
      status_code=404,
      detail="User not found"
    )
    
  db_user.name = user.name if user.name is not None else user.name
  db_user.email = user.email if user.email is not None else user.email
  db.commit()
  db.refresh(db_user)
  return db_user
  
  
@app.delete("/users/{user_id}", response_model=UserResponse, description="Delete user data")
async def delete_user(user_id: int, db: session = Depends(get_db)):
  delete_id = db.query(User).filter(User.id == user_id).first()
  
  if delete_id is None:
    raise HTTPException(
      status_code=404,
      detail="User not Found"
    )
  
  db.delete(delete_id)
  db.commit()
  return delete_id