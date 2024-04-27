######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customer Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customers from the inventory of customers in the CustomerShop
"""
import hashlib
from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Customer, Gender
from service.common import status  # HTTP Status Codes
from . import api


def encrypt_password(password):
    """Hashing Passwords"""
    return hashlib.sha256(password.encode("UTF-8")).hexdigest()


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for root URL")
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S   F O R   C U S T O M E R
######################################################################

# Define the model so that the docs reflect what can be sent
create_customer_model = api.model(
    "Customer",
    {
        "id": fields.Integer(required=True, description="Id of the Customer"),
        "username": fields.String(
            required=True, description="The username of the Customer"
        ),
        "password": fields.String(
            required=True, description="The password of the Customer"
        ),
        "first_name": fields.String(
            required=True, description="The first name of the Customer"
        ),
        "last_name": fields.String(
            required=True, description="The last name of the Customer"
        ),
        "email": fields.String(required=True, description="The email of the Customer"),
        "address": fields.String(
            required=True, description="The address of the Customer"
        ),
        "active": fields.Boolean(required=True, description="Is the Customer active?"),
        # pylint: disable=protected-access
        "gender": fields.String(
            enum=Gender._member_names_, description="The gender of the Customer"
        ),
    },
)

# Define the model so that the docs reflect what can be sent
customer_model = api.inherit(
    "CustomerModel",
    create_customer_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The Id of the customer assigned internally by the service",
        ),
    },
)

# query string arguments for customers
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "username",
    type=str,
    location="args",
    required=False,
    help="List Customers by username",
)
customer_args.add_argument(
    "active",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Customers by active status",
)
customer_args.add_argument(
    "gender", type=str, location="args", required=False, help="List Customers by gender"
)


######################################################################
#  PATH: /customers/{id}
######################################################################
@api.route("/customers/<customer_id>")
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customers/{id} - Returns a Customer with the id
    PUT /customers/{id} - Update a Customer with the id
    DELETE /customers/{id} -  Deletes a Customer with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single Customer

        This endpoint will return a Customer based on it's id
        """
        app.logger.info("Request for customer with id: %s", customer_id)

        customer = Customer.find(customer_id)
        if not customer:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("update_customers")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    # @token_required
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to update customer with id: %d", customer_id)
        check_content_type("application/json")
        # original_password = None
        customer = Customer.find(int(customer_id))
        if not customer:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id: '{customer_id}' was not found.",
            )
        # else:
        original_hashed_password = customer.password

        customer.deserialize(request.get_json())
        customer.id = int(customer_id)

        # Hash the new password if it's different from the original
        if customer.password != original_hashed_password:
            customer.password = encrypt_password(customer.password)
        customer.update(original_hashed_password)

        app.logger.info("Customer with ID: %d updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    # @token_required
    def delete(self, customer_id):
        """
        Delete a Customer

        This endpoint will delete a Customer based the id specified in the path
        """
        app.logger.info("Request to delete customer with id: %d", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()

        app.logger.info("Customer with ID: %d delete complete.", customer_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    # ------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    # ------------------------------------------------------------------
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """Returns all of the Customers by some Attributes"""
        app.logger.info("Request for customer list")

        query = Customer.query

        # if 'username' in request.args:
        #     query = Customer.query_by_username(request.args.get('username'))
        # if 'email' in request.args:
        #     query = Customer.query_by_email(request.args.get('email'))
        # if 'first_name' in request.args:
        #     query = Customer.find_by_name(request.args.get('first_name'))
        # if 'last_name' in request.args:
        #     query = Customer.query_by_last_name(request.args.get('last_name'))
        # if 'address' in request.args:
        #     query = Customer.query_by_address(request.args.get('address'))

        # dynamic querying
        for param in ["username", "email", "address", "first_name", "last_name"]:
            if param in request.args:
                value = request.args.get(param)
                if value.startswith('"') and value.endswith('"'):
                    # Exact search
                    exact_value = value[1:-1]
                    query = query.filter(getattr(Customer, param) == exact_value)
                else:
                    # Fuzzy search
                    query = query.filter(getattr(Customer, param).ilike(f"%{value}%"))

        if "gender" in request.args:
            gender_value = request.args.get("gender").upper()
            if gender_value in Gender.__members__:
                query = query.filter(
                    getattr(Customer, "gender") == Gender[gender_value]
                )
            else:
                error(status.HTTP_400_BAD_REQUEST, "Invalid gender value")

        if "active" in request.args:
            active_value = request.args.get("active").lower()
            if active_value in ["true", "1"]:
                query = query.filter(Customer.active)
            elif active_value in ["false", "0"]:
                query = query.filter(~Customer.active)
            else:
                error(status.HTTP_400_BAD_REQUEST, "Invalid active value")

        customers = query.all()
        results = [customer.serialize() for customer in customers]
        app.logger.info("Returning %d customers", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("create_customers")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_customer_model)
    @api.marshal_with(customer_model, code=201)
    # @token_required
    def post(self):
        """
        Creates a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to Create a Customer")
        check_content_type("application/json")

        customer = Customer()
        customer.deserialize(request.get_json())
        customer.create()

        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )

        app.logger.info("Customer with ID: %d created.", customer.id)
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /customers/{id}/activate
######################################################################
@api.route("/customers/<customer_id>/activate")
@api.param("customer_id", "The Customer identifier")
class ActivateCustomerResource(Resource):
    """Activation actions on a Customer"""

    @api.doc("activate_customers")
    @api.response(404, "Customer not found")
    def put(self, customer_id):
        """
        Activate a customer

        This endpoint will activate a customer based on the id specified in the path
        """
        customer = Customer.find(customer_id)
        if not customer:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.activate()
        return customer.serialize(), status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /customers/{id}/deactivate
######################################################################
@api.route("/customers/<customer_id>/deactivate")
@api.param("customer_id", "The Customer identifier")
class DeactivateCustomerResource(Resource):
    """Deactivation actions on a Customer"""

    @api.doc("deactivate_customers")
    @api.response(404, "Customer not found")
    def put(self, customer_id):
        """
        Deactivate a customer

        This endpoint will deactivate a customer based on the id specified in the path
        """
        customer = Customer.find(customer_id)
        if not customer:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.deactivate()
        return customer.serialize(), status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
