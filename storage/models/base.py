from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Time, DateTime
from sqlalchemy.orm import relationship

STR_SIZE = 256
Base = declarative_base()
