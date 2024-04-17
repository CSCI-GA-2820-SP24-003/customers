"""
Models for YourResourceModel

All of the models are stored in this module
"""

import logging
from enum import Enum
import hashlib
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")


def encrypt_password(password):
    """Hashing Passwords"""
    return hashlib.sha256(password.encode("UTF-8")).hexdigest()


# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class Gender(Enum):
    """Enumeration of valid Genders"""

    MALE = 0
    FEMALE = 1
    UNKNOWN = 3


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


# pylint: disable=too-many-instance-attributes


class Customer(db.Model):
    """
    Class that represents Customers
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(
        db.Enum(Gender), nullable=False, server_default=(Gender.UNKNOWN.name)
    )
    active = db.Column(db.Boolean(), nullable=False, default=False)
    address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Customer {self.first_name, self.last_name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """

        # id is checked by database itself
        if Customer.query.filter_by(username=self.username).first():
            raise DataValidationError(f"Username {self.username} is already in use.")
        if Customer.query.filter_by(email=self.email).first():
            raise DataValidationError(f"Email {self.email} is already in use.")

        logger.info("Creating %s", self.first_name)
        self.id = None  # pylint: disable=invalid-name
        self.password = encrypt_password(self.password)
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self, original_password=None):
        """
        Updates a Customer to the database
        """
        existing_user = Customer.query.filter(
            (Customer.username == self.username) | (Customer.email == self.email),
            Customer.id != self.id).first()
        
        if existing_user:
            if existing_user.username == self.username:
                raise DataValidationError("Username already exists with another account")
            if existing_user.email == self.email:
                raise DataValidationError("Email already exists with another account")
        
        logger.info("Saving %s", self.first_name)
        if self.id is None:
            raise DataValidationError("There is no valid ID Specified")
        # if PWD changed, hash again
        if original_password is not None and not original_password == self.password:
            self.password = encrypt_password(self.password)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.first_name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender.name,
            "active": self.active,
            "address": self.address,
            "email": self.email,
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """

        try:
            # self.id = data["id"]
            self.username = data["username"]
            self.password = data["password"]
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.gender = getattr(Gender, data["gender"])
            if isinstance(data["active"], bool):
                self.active = data["active"]
            else:
                raise DataValidationError("Invalid type for active Boolean")
            self.address = data["address"]
            self.email = data["email"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    def activate(self):
        """Activates the customer account"""
        self.active = True
        self.update()

    def deactivate(self):
        """Deactivates the customer account"""
        self.active = False
        self.update()

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Customer in the database"""
        logger.info("Processing all Customer")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, first_name):
        """Returns all Customer with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", first_name)
        return cls.query.filter(cls.first_name == first_name)

    @classmethod
    def query_by_last_name(cls, last_name):
        """It should return a list of all customers with a certain last_name"""
        logger.info("Processing lookup for %s ...", last_name)
        return cls.query.filter(cls.last_name == last_name)

    @classmethod
    def query_by_active(cls, active):
        """It should return a list of all active/inactive customers"""
        logger.info("Processing lookup for %s ...", active)
        return cls.query.filter(cls.active == active)

    @classmethod
    def query_by_gender(cls, gender):
        """It should return a list of all customers when given a gender"""
        logger.info("Processing lookup for %s ...", gender)
        return cls.query.filter(cls.gender == gender)

    @classmethod
    def query_by_address(cls, address):
        """It should return a list of all customers with a certain address"""
        logger.info("Processing lookup for %s ...", address)
        return cls.query.filter(cls.address == address)

    @classmethod
    def query_by_username(cls, username):
        """It should return a list of all customers with a certain username"""
        logger.info("Processing lookup for %s ...", username)
        return cls.query.filter(cls.username == username)

    @classmethod
    def query_by_email(cls, email):
        """It should return a list of all customers with a certain email"""
        logger.info("Processing lookup for %s ...", email)
        return cls.query.filter(cls.email == email)
