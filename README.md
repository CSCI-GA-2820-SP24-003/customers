# NYU DevOps Project Customer Squad

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is the Customers Squad's project.
The customers service is a representation of the customers account of the eCommerce site.

## Description

The Customer Store Service is a REST API designed to manage the inventory of customers in the CustomerShop. It allows users to perform basic CRUD (Create, Read, Update, Delete) operations on customer data.


This project contains the instructions and code for Customers microservice. The `/service` folder contains our `models.py` file for our model and a `routes.py` file for our service. The `/tests` folder has test case code for testing the model and the service separately.


## Database Schema

| Column | Data type | Condition |
| --- | --- | --- |
| `id` | `<integer>` | `Primary Key, id > 0` |
| `username` | `<string>` | `Not null` |
| `password` | `<string>` | `Not null` |
| `first_name` | `<string>` | `Not null` |
| `last_name` | `<string>` | `Not null` |
| `gender` | `<enum>` | `Not null` |
| `active` | `<boolean>` | `Not null, Default: False` |
| `address` | `<string>` | `Not null` |
| `email` | `<string>` | `Not null` |


### Constraints and Conditions:
1. id: Must be an integer greater than 0.

2. username, password, first_name, last_name, address, and email: Must be non-empty strings.

3. gender: Must be one of the predefined values in the Gender enum.

4. active: Default value is False.

### Gender Enum
The Gender enum defines the possible genders:

`MALE`
`FEMALE`
`UNKNOWN`

## API Endpoints

### Overview

Our service implements the following functionalities:

1. Root URL Response: Provides useful information about the service in JSON format.
2. Retrieve a Customer: Retrieves a single customer based on the provided customer ID.
3. Create a Customer: Creates a new customer based on the data provided in the request body.
4. Delete a Customer: Deletes a customer based on the provided customer ID.
5. List All Customers: Returns a list of all customers.
6. Update an Existing Customer: Updates an existing customer based on the provided data in the request body.

### Root URL
GET /: Root URL response.

### Customer Endpoints

| Method | URI | Description |
| --- | --- | ------ | 
| `GET` | `/customers/<customer_id>` | Retrieve a single customer with the given `id`. |
| `POST` | `/customers` | Create a new customer. |
| `DELETE` | `/customers/<customer_id>` | Delete a customer with the given `id`. |
| `GET` | `/customers` | List all customers. |
| `PUT` | `/customers/<customer_id>` | Update an existing customer with the given `id`. |

### Usage

1. Create a Customer: 
   
   Send a POST request to /customers with JSON data containing details of the new customer.

2. Retrieve a Customer: 
   
   Send a GET request to /customers/<customer_id> to retrieve details of a specific customer.

3. Delete a Customer: 
   
   Send a DELETE request to /customers/<customer_id> to delete a specific customer.

4. List All Customers: 
   
   Send a GET request to /customers to retrieve a list of all customers.

5. Update an Existing Customer: 
   
   Send a PUT request to /customers/<customer_id> with JSON data containing updated details of the customer.

### Error Handling
The service provides appropriate error handling, returning relevant HTTP status codes and error messages when necessary.

## Files
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
