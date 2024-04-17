"""
Test cases for Customer Model
"""

import os
import logging
import hashlib
from unittest import TestCase
from unittest.mock import patch
from tests.customer_factory import CustomerFactory
from wsgi import app
from service.models import Customer, DataValidationError, db, Gender


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/cdb"
)


######################################################################
#  C U S T O M E R   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestCustomer(TestCase):
    """Test Cases for customer Model"""

    # pylint: disable=R0801
    # Disable pylint message R0801 (similar lines in 2 files) for the following block
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    # pylint: enable=R0801
    # Re-enable pylint message R0801 (similar lines in 2 files) after the block of code

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_customer(self):
        """It should Create an account and assert it exists"""
        customer = Customer(
            username="fidodog",
            password="123456789",
            first_name="Fido",
            last_name="Dog",
            gender=Gender.MALE,
            active=True,
            address="1660 Broadway Street, NY, NY",
        )
        self.assertEqual(customer.username, "fidodog")
        self.assertEqual(customer.password, "123456789")
        self.assertTrue(customer is not None)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.first_name, "Fido")
        self.assertEqual(customer.last_name, "Dog")
        self.assertEqual(customer.active, True)
        self.assertEqual(customer.gender, Gender.MALE)
        self.assertTrue(customer.address is not None)
        customer = Customer(
            username="fidodog",
            password="123456789",
            first_name="Fido",
            last_name="Dog",
            gender=Gender.FEMALE,
            active=False,
            address="1660 Broadway Street, NY, NY",
        )
        self.assertEqual(customer.active, False)
        self.assertEqual(customer.gender, Gender.FEMALE)

    def test_create_customer_exception(self):
        """It should handle exception when creating a Customer fails"""
        customer = CustomerFactory()
        self.assertTrue(customer.id is None or customer.id == 0)

        with patch("service.models.db.session.add") as mock_add, patch(
            "service.models.db.session.commit"
        ) as mock_commit:
            # Configure the mock to raise an exception when commit is called
            mock_commit.side_effect = Exception("Simulated database error")

            with self.assertRaises(DataValidationError):
                customer.create()

            # Assert db.session.rollback is called after an exception
            mock_add.assert_called_once_with(customer)
            mock_commit.assert_called_once()

    def test_add_a_customer(self):
        """It should Create a customer and add it to the database"""
        customer = Customer.all()
        self.assertEqual(customer, [])
        customer = Customer(
            username="fidodog",
            password="123456789",
            first_name="Fido",
            last_name="Dog",
            gender=Gender.MALE,
            active=True,
            address="1660 Broadway Street, NY, NY",
            email="myname@gmail.com",
        )
        self.assertTrue(customer is not None)
        self.assertEqual(customer.id, None)
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customer = Customer.all()
        self.assertEqual(len(customer), 1)

    def test_create_with_duplicate_username(self):
        """It should not create a customer with a duplicate username"""
        customer1 = CustomerFactory(username="user123", email="123@example.com")
        customer1.create()

        customer2 = CustomerFactory(username="user123", email="456@example.com")  
        with self.assertRaises(DataValidationError) as context:
            customer2.create()

        self.assertIn('Username user123 is already in use', str(context.exception))

    def test_create_with_duplicate_email(self):
        """It should not create a customer with a duplicate email"""
        customer1 = CustomerFactory(username="user123", email="123@example.com")
        customer1.create()

        customer2 = CustomerFactory(username="user456", email="123@example.com")  
        with self.assertRaises(DataValidationError) as context:
            customer2.create()

        self.assertIn('Email 123@example.com is already in use', str(context.exception))

    def test_read_a_customer(self):
        """It should Read a customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        self.assertIsNotNone(customer.id)
        # Fetch it back
        found_customer = Customer.find(customer.id)
        self.assertEqual(found_customer.id, customer.id)
        self.assertEqual(found_customer.username, customer.username)
        self.assertEqual(found_customer.password, customer.password)
        self.assertEqual(found_customer.first_name, customer.first_name)
        self.assertEqual(found_customer.last_name, customer.last_name)
        self.assertEqual(found_customer.gender, customer.gender)
        self.assertEqual(found_customer.active, customer.active)
        self.assertEqual(found_customer.address, customer.address)
        self.assertEqual(found_customer.email, customer.email)

    def test_update_a_customer(self):
        """It should Update a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        logging.debug(customer)
        self.assertIsNotNone(customer.id)
        # Change it an save it
        customer.first_name = "Jack"
        original_id = customer.id
        original_password = customer.password
        new_password = "new password"
        customer.password = new_password
        customer.update(original_password)
        hashed_new_password = hashlib.sha256(new_password.encode("UTF-8")).hexdigest()
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.first_name, "Jack")
        self.assertEqual(customer.password, hashed_new_password)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, original_id)
        self.assertEqual(customers[0].first_name, "Jack")
        self.assertEqual(customers[0].password, hashed_new_password)

    def test_update_no_id(self):
        """It should not Update a Customer with no id"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        self.assertRaises(DataValidationError, customer.update)

    def test_update_customer_exception(self):
        """It should handle exception when updating a Customer fails"""
        customer = CustomerFactory()
        customer.id = 1
        with patch("service.models.db.session.commit") as mock_commit:
            # Configure the mock to raise an exception when commit is called
            mock_commit.side_effect = Exception("Simulated database error")

            with self.assertRaises(DataValidationError):
                customer.update()

            # Assert db.session.rollback is called after an exception
            mock_commit.assert_called_once()

    def test_update_with_duplicate_username(self):
        """It should not create a customer with a duplicate username"""
        CustomerFactory(username="user123").create()
        
        customer2 = CustomerFactory(username="user456")
        customer2.create()

        customer2.username = "user123"
        with self.assertRaises(DataValidationError) as context:
            customer2.update()

        self.assertIn('Username already exists with another account', str(context.exception))

    def test_update_with_duplicate_email(self):
        """It should not create a customer with a duplicate email"""
        CustomerFactory(email="123@example.com").create()
        
        customer2 = CustomerFactory(email="456@example.com")
        customer2.create()

        customer2.email = "123@example.com"
        with self.assertRaises(DataValidationError) as context:
            customer2.update()

        self.assertIn('Email already exists with another account', str(context.exception))

    def test_delete_a_customer(self):
        """It should Delete a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(Customer.all()), 1)
        # delete the customer and make sure it isn't in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    def test_delete_customer_exception(self):
        """It should handle exception when deleting a Customer fails"""
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(Customer.all()), 1)

        with patch("service.models.db.session.delete") as mock_delete, patch(
            "service.models.db.session.commit"
        ) as mock_commit:
            # Configure the mock to raise an exception when commit is called
            mock_commit.side_effect = Exception("Simulated database error")

            with self.assertRaises(DataValidationError):
                customer.delete()

            # Assert db.session.rollback is called after an exception
            mock_delete.assert_called_once_with(customer)
            mock_commit.assert_called_once()

    def test_list_all_customers(self):
        """It should List all Customers in the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        # Create 5 Customers
        for _ in range(5):
            customer = CustomerFactory()
            customer.create()
        # See if we get back 5 customers
        customers = Customer.all()
        self.assertEqual(len(customers), 5)

    def test_serialize_a_customer(self):
        """It should serialize a Customer"""
        customer = CustomerFactory()
        data = customer.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], customer.id)
        self.assertIn("username", data)
        self.assertEqual(data["username"], customer.username)
        self.assertIn("password", data)
        self.assertEqual(data["password"], customer.password)
        self.assertIn("first_name", data)
        self.assertEqual(data["first_name"], customer.first_name)
        self.assertIn("last_name", data)
        self.assertEqual(data["last_name"], customer.last_name)
        self.assertIn("gender", data)
        self.assertEqual(data["gender"], customer.gender.name)
        self.assertIn("active", data)
        self.assertEqual(data["active"], customer.active)
        self.assertIn("address", data)
        self.assertEqual(data["address"], customer.address)
        self.assertIn("email", data)
        self.assertEqual(data["email"], customer.email)

    def test_deserialize_a_customer(self):
        """It should de-serialize a Customer"""
        data = CustomerFactory().serialize()
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        # self.assertEqual(customer.id, data["id"])
        self.assertEqual(customer.username, data["username"])
        self.assertEqual(customer.password, data["password"])
        self.assertEqual(customer.first_name, data["first_name"])
        self.assertEqual(customer.last_name, data["last_name"])
        self.assertEqual(customer.gender.name, data["gender"])
        self.assertEqual(customer.active, data["active"])
        self.assertEqual(customer.address, data["address"])
        self.assertEqual(customer.email, data["email"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Customer with missing data"""
        data = {
            "id": 1,
            "username": "Friend",
            "first_name": "Fido",
            "last_name": "dude",
        }
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        data["active"] = "true"
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_bad_gender(self):
        """It should not deserialize a bad gender attribute"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        data["gender"] = "male"  # wrong case
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_representing_a_customer(self):
        """When trying to represent a customer, it should return the correct string"""
        test_customer = CustomerFactory()
        customer_output = repr(test_customer)
        self.assertEqual(
            customer_output,
            f"<Customer {test_customer.first_name, test_customer.last_name} id=[{test_customer.id}]>",
        )

    def test_deactivate_a_customer(self):
        """It should Deactivate a Customer"""
        customer = CustomerFactory()
        customer.active = True
        self.assertTrue(customer.active)
        customer.deactivate()
        self.assertFalse(customer.active)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestCase):
    """Setup and Tear down for test cases"""

    # pylint: disable=R0801
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_find_customer(self):
        """It should Find a Customer by ID"""
        customers = CustomerFactory.create_batch(5)
        for customer in customers:
            customer.create()
        logging.debug(customers)
        # make sure they got saved
        self.assertEqual(len(Customer.all()), 5)
        # find the 2nd customer in the list
        customer = Customer.find(customers[1].id)
        self.assertIsNot(customer, None)
        self.assertEqual(customer.id, customers[1].id)
        self.assertEqual(customer.username, customers[1].username)
        self.assertEqual(customer.first_name, customers[1].first_name)
        self.assertEqual(customer.last_name, customers[1].last_name)
        self.assertEqual(customer.username, customers[1].username)
        self.assertEqual(customer.password, customers[1].password)
        self.assertEqual(customer.gender.name, customers[1].gender.name)
        self.assertEqual(customer.active, customers[1].active)
        self.assertEqual(customer.address, customers[1].address)
        self.assertEqual(customer.email, customers[1].email)

    def test_find_by_name(self):
        """It should Find a Customer by Name"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        first_name = customers[0].first_name
        count = len(
            [customer for customer in customers if customer.first_name == first_name]
        )
        found = Customer.find_by_name(first_name)
        self.assertEqual(found.count(), count)
        for customer in found:
            self.assertEqual(customer.first_name, first_name)

    def test_query_by_last_name(self):
        """It should return a list of all customers with the specified last_name."""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        logging.debug(customers)
        last_name = customers[0].last_name
        count = len(
            [customer for customer in customers if customer.last_name == last_name]
        )
        query = Customer.query_by_last_name(last_name)

        self.assertEqual(query.count(), count)
        for customer in query:
            self.assertEqual(customer.last_name, last_name)

    def test_query_by_active(self):
        """It should list all customers by active/inactive boolean"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        active = customers[0].active
        count = len([customer for customer in customers if customer.active == active])
        query = Customer.query_by_active(active)

        self.assertEqual(query.count(), count)
        for customer in query:
            self.assertEqual(customer.active, active)

    def test_query_by_gender(self):
        """It should return a list of all customers with the specified gender."""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        logging.debug(customers)
        gender = customers[0].gender.name
        count = len(
            [customer for customer in customers if customer.gender.name == gender]
        )
        query = Customer.query_by_gender(gender)

        self.assertEqual(query.count(), count)
        for customer in query:
            self.assertEqual(customer.gender.name, gender)

    def test_query_by_address(self):
        """It should return a list of all customers with the specified address."""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        logging.debug(customers)
        address = customers[0].address
        count = len([customer for customer in customers if customer.address == address])
        query = Customer.query_by_address(address)

        self.assertEqual(query.count(), count)
        for customer in query:
            self.assertEqual(customer.address, address)

    def test_query_by_username(self):
        """It should Find a Customer by Username"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        username = customers[0].username
        count = len(
            [customer for customer in customers if customer.username == username]
        )
        found = Customer.query_by_username(username)
        self.assertEqual(found.count(), count)
        for customer in found:
            self.assertEqual(customer.username, username)

    def test_query_by_email(self):
        """It should return a list of all customers with the specified email."""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        # logging.debug(customers)
        email = customers[0].email
        count = len([customer for customer in customers if customer.email == email])
        query = Customer.query_by_email(email)

        self.assertEqual(query.count(), count)
        for customer in query:
            self.assertEqual(customer.email, email)
