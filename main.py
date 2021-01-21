from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from sqlalchemy.orm import Session

from auth.auth_user import Token, authenticate_user, create_access_token, get_current_active_user
from auth.schemas import AuthUsersBase
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from database import engine, SessionLocal
from dogs import models, schemas, crud
from users import models as model_users, schemas as schemas_users, crud as crud_users
from auth import models as model_auth_users
from mangum import Mangum
import requests

"""
     ********  creating models  ***********
"""

model_users.Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine)
model_auth_users.Base.metadata.create_all(bind=engine)

app = FastAPI()

"""
     ********  creating database dependency  ***********
"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
     ********  authentication system  ***********
"""


@app.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


"""
     ********  endpoints for the dog entity  ***********
"""


@app.get("/api/dogs", response_model=List[schemas.Dogs])
def read_dogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dogs = crud.get_dogs(db, skip=skip, limit=limit)
    if not dogs:
        raise HTTPException(status_code=200, detail="No pets registered")
    return dogs


@app.get("/api/dogs/{name}", response_model=schemas.Dogs)
def read_dog(name: str, db: Session = Depends(get_db)):
    db_dog = crud.get_dog(db, dog_name=name)
    if db_dog is None:
        raise HTTPException(status_code=404, detail="Dog not found")
    return db_dog


@app.get("/api/dogs/is_adopted", response_model=List[schemas.Dogs])
def read_dogs(is_adopted: bool = True, db: Session = Depends(get_db)):
    dogs = crud.get_dog_by_is_adopted(db, is_adopted=is_adopted)
    if not dogs:
        raise HTTPException(status_code=404, detail="There are no dogs for adoption.")
    return dogs


@app.post("/api/dogs/{name}", response_model=schemas.Dogs)
def create_dogs(dog: schemas.DogsCreate, db: Session = Depends(get_db),
                current_user: AuthUsersBase = Depends(get_current_active_user)):
    db_dog = crud.get_dog_by_name(db, name=dog.name)
    db_user = crud_users.get_user(db, id_user=dog.id_user)
    if db_user:
        if db_dog:
            raise HTTPException(status_code=400, detail="Dog already registered")
        get_picture = requests.get('http://dog.ceo/api/breeds/image/random').json()
        if not get_picture:
            raise HTTPException(status_code=503, detail="there was an error loading picture.")
        dog.picture = get_picture.get('message')
        if crud.create_dog(db=db, dog=dog):
            raise HTTPException(status_code=200, detail="Dog entered successfully.")
    else:
        raise HTTPException(status_code=404, detail="User not found.")


@app.put("/api/dogs/{name}", response_model=schemas.Dogs)
def edit_dogs(name: str, dog: schemas.DogsCreate, db: Session = Depends(get_db),
              current_user: AuthUsersBase = Depends(get_current_active_user)):
    db_dog = crud.update_dog(db, dog_name=name, dog_update=dog)
    if db_dog is None:
        raise HTTPException(status_code=404, detail="Dog not found")
    return db_dog


@app.delete("/api/dogs/{name}")
def delete_dogs(name: str, db: Session = Depends(get_db),
                current_user: AuthUsersBase = Depends(get_current_active_user)):
    db_dog = crud.get_dog_by_name(db, name=name)
    if db_dog:
        dog_delete = crud.delete_dog(db, dog_name=name)
        if dog_delete:
            raise HTTPException(status_code=200, detail="dog successfully remove.")
    else:
        raise HTTPException(status_code=404, detail="Dog not found")


"""
     ********  endpoints for the user entity  ***********
"""


@app.get("/api/users", response_model=List[schemas_users.Users])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud_users.get_users(db, skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=200, detail="No users registered")
    return users


@app.post("/api/users/{id_user}", response_model=schemas_users.Users)
def create_user(id_user: int, user: schemas_users.UsersCreate, db: Session = Depends(get_db),
                current_user: AuthUsersBase = Depends(get_current_active_user)):
    db_user = crud_users.get_user(db, id_user=id_user)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    if crud_users.create_user(db=db, user=user):
        raise HTTPException(status_code=200, detail="User entered successfully.")


@app.put("/api/users/{id_user}", response_model=schemas_users.Users)
def edit_user(id_user: int, user: schemas_users.UsersCreate, db: Session = Depends(get_db),
              current_user: AuthUsersBase = Depends(get_current_active_user)):
    db_user = crud_users.update_user(db, id_user=id_user, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/api/users/{id_user}")
def delete_user(id_user: int, db: Session = Depends(get_db),
                current_user: AuthUsersBase = Depends(get_current_active_user)):
    db_user = crud_users.get_user(db, id_user=id_user)
    if db_user:
        user_delete = crud_users.delete_user(db, id_user=id_user)
        if user_delete:
            raise HTTPException(status_code=200, detail="User successfully remove.")
    else:
        raise HTTPException(status_code=404, detail="User not found")


handler = Mangum(app, enable_lifespan=False)
