from sqlalchemy.orm import Session

from users import models, schemas


def get_user(db: Session, id_user: int):
    return db.query(models.User).filter(models.User.id == id_user).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UsersCreate):
    db_users = models.User(name=user.name, last_name=user.last_name, email=user.email)
    db.add(db_users)
    db.commit()
    db.refresh(db_users)
    return db_users


def update_user(db: Session, id_user: int, user_update: schemas.UsersCreate):
    user = db.query(models.User).filter(models.User.id == id_user).first()
    if user:
        user.name = user_update.name
        user.last_name = user_update.last_name
        user.email = user_update.email
        db.commit()
        db.refresh(user)
        return user
    else:
        return None


def delete_user(db: Session, id_user: int):
    user = db.query(models.User).filter(models.User.id == id_user).first()
    db.delete(user)
    db.commit()
    return True
