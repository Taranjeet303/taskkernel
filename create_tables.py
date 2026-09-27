from db.session import engine
from models.models import Base
import models.models


Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")