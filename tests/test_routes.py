"""
TestCustomerModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Customer
from .customer_factory import CustomerFactory
# from unittest.mock import patch

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_customers(self, count):
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test customer",
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["username"], test_customer.username)
        self.assertEqual(new_customer["password"], test_customer.password)
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["gender"], test_customer.gender.name)
        self.assertEqual(new_customer["active"], test_customer.active)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["email"], test_customer.email)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["username"], test_customer.username)
        self.assertEqual(new_customer["password"], test_customer.password)
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["gender"], test_customer.gender.name)
        self.assertEqual(new_customer["active"], test_customer.active)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["email"], test_customer.email)

    def test_delete_customer(self):
        """It should Delete a Customer"""
        test_customer = self._create_customers(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        logging.debug(new_customer)
        new_customer["username"] = "unknown"
        new_customer["password"] = "new_password"
        new_customer["first_name"] = "new_first_name"
        new_customer["last_name"] = "new_last_name"
        new_customer["address"] = "new_address"
        new_customer["email"] = "new_email"

        response = self.client.put(
            f"{BASE_URL}/{new_customer['id']}", json=new_customer
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = response.get_json()
        self.assertEqual(updated_customer["username"], "unknown")
        self.assertEqual(new_customer["password"], "new_password")
        self.assertEqual(new_customer["first_name"], "new_first_name")
        self.assertEqual(new_customer["last_name"], "new_last_name")
        self.assertEqual(new_customer["address"], "new_address")
        self.assertEqual(new_customer["email"], "new_email")
        # self.assertEqual(updated_customer.active, True)
        # self.assertEqual(updated_customer.gender, Gender.MALE)
        # self.assertTrue(updated_customer.address is not None)

    def test_get_customer_not_found(self):
        """It should Return Not Found when the Customer does not exist"""
        non_existent_customer_id = 9999
        response = self.client.get(f"{BASE_URL}/{non_existent_customer_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        error_response = response.get_json()
        self.assertIn("was not found", error_response["message"])

    def test_get_customer_success(self):
        """It should Retrieve an existing Customer"""
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_customer = response.get_json()
        response = self.client.get(f"{BASE_URL}/{new_customer['id']}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        retrieved_customer = response.get_json()
        self.assertEqual(retrieved_customer["id"], new_customer["id"])
        self.assertEqual(retrieved_customer["first_name"], test_customer.first_name)
        self.assertEqual(retrieved_customer["last_name"], test_customer.last_name)
        self.assertEqual(retrieved_customer["username"], test_customer.username)
        self.assertEqual(retrieved_customer["password"], test_customer.password)
        self.assertEqual(retrieved_customer["address"], test_customer.address)
        self.assertEqual(retrieved_customer["email"], test_customer.email)

    def test_data_validation_error(self):
        """It should return a status code for an Invalid Field"""
        response = self.client.post(
            "/customers", json={"invalid_field": "invalid_value"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bad Request", response.json["error"])

    def test_bad_request(self):
        """It should return the correct bad request"""
        response = self.client.post(
            "/customers", data="This is not JSON", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bad Request", response.json["error"])

    def test_method_not_supported(self):
        """It should return the correct method not allowed"""
        response = self.client.put("/")
        self.assertEqual(response.status_code, 405)
        self.assertIn("Method not Allowed", response.json["error"])

    def test_mediatype_not_supported(self):
        """It should return that the datatype is not supported"""
        response = self.client.post("/customers", data="{}", content_type="text/plain")
        self.assertEqual(response.status_code, 415)
        self.assertIn("Unsupported media type", response.json["error"])
