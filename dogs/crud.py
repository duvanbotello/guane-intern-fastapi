from sqlalchemy.orm import Session

from dogs import models, schemas


def get_dog(db: Session, dog_name: str):
    return db.query(models.Dog).filter(models.Dog.name == dog_name).first()


def get_dog_by_name(db: Session, name: str):
    return db.query(models.Dog).filter(models.Dog.name == name).first()


def get_dog_by_is_adopted(db: Session, is_adopted: bool):
    return db.query(models.Dog).filter(models.Dog.is_adopted == is_adopted).all()


def get_dogs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Dog).offset(skip).limit(limit).all()


def create_dog(db: Session, dog: schemas.DogsCreate):
    db_dog = models.Dog(name=dog.name, picture=dog.picture, create_date=dog.create_date, is_adopted=dog.is_adopted,
                        id_user=dog.id_user)
    db.add(db_dog)
    db.commit()
    db.refresh(db_dog)
    return db_dog


def update_dog(db: Session, dog_name: str, dog_update: schemas.DogsCreate):
    dog = db.query(models.Dog).filter(models.Dog.name == dog_name).first()
    if dog:
        dog.name = dog_update.name
        dog.picture = dog_update.picture
        dog.create_date = dog_update.create_date
        dog.is_adopted = dog_update.is_adopted
        db.commit()
        db.refresh(dog)
        return dog
    else:
        return None


def delete_dog(db: Session, dog_name: str):
    dog = db.query(models.Dog).filter(models.Dog.name == dog_name).first()
    db.delete(dog)
    db.commit()
    return True
