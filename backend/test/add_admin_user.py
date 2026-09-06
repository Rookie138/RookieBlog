from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.auth.model import User
from app.config.setting import settings
from app.utils.hash_util import PwdHashUtil


def add_user():
    username = 'admin'
    password = '123456'
    name = 'admin'
    hashed_password = PwdHashUtil.hash_password(password)
    user = User(username=username, password=hashed_password, name=name)
    engine = create_engine(settings.DB_URI)
    SyncSessionLocal = sessionmaker(bind=engine,expire_on_commit=False)
    with SyncSessionLocal() as session:
        session.add(user)
        session.commit()
        session.flush()
        session.refresh(user)


if __name__ == '__main__':

    try:
        add_user()
    except Exception as err:
        print(err)