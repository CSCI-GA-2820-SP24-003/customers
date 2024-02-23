"""
Models for YourResourceModel

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import date

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class Gender(Enum):
    """Enumeration of valid Pet Genders"""

    MALE = 0
    FEMALE = 1
    UNKNOWN = 3


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Customer(db.Model):
    """
    Class that represents Customers
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(63), nullable = False)
    last_name = db.Column(db.String(63), nullable = False)
    gender = db.Column(
        db.Enum(Gender), nullable=False, server_default=(Gender.UNKNOWN.name)
    )
    birthday = db.Column(db.Date(), nullable=False, default=date.today())
    active = db.Column(db.boolean(), nullable = False, default = False)
    address = db.column(db.string(63), nullable = False)




    def __repr__(self):
        return f"<YourResourceModel {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a YourResourceModel to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """ Removes a YourResourceModel from the data store """
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """ Serializes a YourResourceModel into a dictionary """
        return {"id": self.id, "name": self.name}

    def deserialize(self, data):
        """
        Deserializes a YourResourceModel from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """ Returns all of the YourResourceModels in the database """
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a YourResourceModel by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
