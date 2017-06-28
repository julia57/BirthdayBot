from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from telegram.ext import Updater


engine = create_engine('sqlite:///blog.sqlite2')
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

updater = Updater("340284668:AAFjrHr7B8ovQE8op62RcakCe-07pXyhF3c")
dp = updater.dispatcher
job_queue = updater.job_queue
