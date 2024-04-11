"""
TestCustomerModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
import hashlib
from wsgi import app
from service.common import status
from service.models import db, Customer
from .customer_factory import CustomerFactory


# from unittest.mock import patch


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


def encrypt_password(password):
    """Hashing Password"""
    return hashlib.sha256(password.encode("UTF-8")).hexdigest()


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
# pylint: disable=R0801


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

    def test_health(self):
        """It should get the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        # logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["username"], test_customer.username)
        # self.assertEqual(new_customer["password"], encrypt_password(test_customer.password))
        # Compare hashed password with the original hashed password
        hashed_password = encrypt_password(test_customer.password)
        self.assertEqual(new_customer["password"], hashed_password)
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
        # self.assertEqual(new_customer["password"], encrypt_password(test_customer.password))
        self.assertEqual(new_customer["password"], hashed_password)
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

    def test_get_customer_list_with_username(self):
        """It should filter customers by username"""
        CustomerFactory(username="user123").create()
        CustomerFactory(username="user456").create()
        CustomerFactory(username="user789").create()

        response = self.client.get(f"{BASE_URL}?username=user123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["username"], "user123")

    def test_get_customer_list_with_email(self):
        """It should filter customers by email"""
        CustomerFactory(email="123@gmail.com").create()
        CustomerFactory(email="456@gmail.com").create()
        CustomerFactory(email="789@gmail.com").create()

        response = self.client.get(f"{BASE_URL}?email=123@gmail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], "123@gmail.com")

    def test_get_customer_list_with_first_name(self):
        """It should filter customers by first name"""
        customers = CustomerFactory.create_batch(2)
        for customer in customers:
            customer.first_name = "name123"
            customer.create()
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.first_name = "name456"
            customer.create()
        customers = CustomerFactory.create_batch(4)
        for customer in customers:
            customer.first_name = "name789"
            customer.create()

        response = self.client.get(f"{BASE_URL}?first_name=name123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["first_name"], "name123")

    def test_get_customer_list_with_last_name(self):
        """It should filter customers by last name"""
        customers = CustomerFactory.create_batch(2)
        for customer in customers:
            customer.last_name = "name123"
            customer.create()
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.last_name = "name456"
            customer.create()
        customers = CustomerFactory.create_batch(4)
        for customer in customers:
            customer.last_name = "name789"
            customer.create()

        response = self.client.get(f"{BASE_URL}?last_name=name123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["last_name"], "name123")

    def test_get_customer_list_with_address(self):
        """It should filter customers by address"""
        customers = CustomerFactory.create_batch(2)
        for customer in customers:
            customer.address = "123 Main St"
            customer.create()
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.address = "456 Main St"
            customer.create()
        customers = CustomerFactory.create_batch(4)
        for customer in customers:
            customer.address = "789 Main St"
            customer.create()

        response = self.client.get(f"{BASE_URL}?address=123 Main St")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["address"], "123 Main St")

    def test_get_customer_list_with_gender(self):
        """It should filter customers by gender"""
        customers = CustomerFactory.create_batch(2)
        for customer in customers:
            customer.gender = "MALE"
            customer.create()
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.gender = "FEMALE"
            customer.create()
        customers = CustomerFactory.create_batch(4)
        for customer in customers:
            customer.gender = "UNKNOWN"
            customer.create()

        response = self.client.get(f"{BASE_URL}?gender=MALE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["gender"], "MALE")

    def test_get_customer_list_with_active_status(self):
        """It should filter customers by active status"""
        customers = CustomerFactory.create_batch(2)
        for customer in customers:
            customer.active = True
            customer.create()
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.active = False
            customer.create()

        response = self.client.get(f"{BASE_URL}?active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)

        response = self.client.get(f"{BASE_URL}?active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_get_customer_list_with_invalid_gender(self):
        """It should return an error for invalid gender value"""
        response = self.client.get(f"{BASE_URL}?gender=NOT_A_GENDER")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Invalid gender value", data["error"])

    def test_get_customer_list_with_invalid_active(self):
        """It should return an error for invalid active value"""
        response = self.client.get(f"{BASE_URL}?active=not_a_boolean")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Invalid active value", data["error"])

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
        self.assertEqual(
            retrieved_customer["password"], encrypt_password(test_customer.password)
        )
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

    def test_activate_customer(self):
        """It should Deactivate a Customer"""
        test_customer_data = CustomerFactory().serialize()
        test_customer_data["active"] = False

        # Create customer via POST request
        create_response = self.client.post(BASE_URL, json=test_customer_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        created_customer = create_response.get_json()

        # Activate the customer via PUT request
        response = self.client.put(f"{BASE_URL}/{created_customer['id']}/activate")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Fetch the customer to verify it's activated
        get_response = self.client.get(f"{BASE_URL}/{created_customer['id']}")

        activated_customer = get_response.get_json()
        self.assertTrue(activated_customer["active"])

    def test_deactivate_customer(self):
        """It should Deactivate a Customer"""
        test_customer_data = CustomerFactory().serialize()
        test_customer_data["active"] = True
        # Create customer via POST request
        create_response = self.client.post(BASE_URL, json=test_customer_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        created_customer = create_response.get_json()

        # Deactivate the customer via PUT request
        response = self.client.put(f"{BASE_URL}/{created_customer['id']}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Fetch the customer to verify it's deactivated
        get_response = self.client.get(f"{BASE_URL}/{created_customer['id']}")
        deactivated_customer = get_response.get_json()
        self.assertFalse(deactivated_customer["active"])

    def test_activate_does_not_exist(self):
        """It should return 404 if the customer does not exist"""
        non_existent_customer_id = 999999
        response = self.client.put(f"{BASE_URL}/{non_existent_customer_id}/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_nonexistent_customer(self):
        """It should return 404 for a nonexistent customer"""
        nonexistent_customer_id = 99999
        response = self.client.put(f"{BASE_URL}/{nonexistent_customer_id}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
