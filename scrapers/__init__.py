# /scrapers/__init__.py

from .Jobberman import jobberman
from .Linkedln import linkedln
from .hotnigerianjobs import hotnigerianjobs
from .Jobsguru import Jobsguru
from .MyJobMag import MyJobMag

# This tells Python which functions are public when someone 
# imports * from this package
__all__ = [
    "linkedln",
    "jobberman",
    "hotnigerianjobs",
    "Jobsguru",
    "MyJobMag"
]