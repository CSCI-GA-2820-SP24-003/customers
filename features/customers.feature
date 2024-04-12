Feature: The customer service back-end
    As a Customer Admin
    I need a RESTful catalog service
    So that I can keep track of all my customers

Background:
    Given the following customers
        | id         | username | password  | first_name | last_name  | gender   | active | address     | email            |
        | 1          | kaite5   | doggy     | Kate       | Wexler     | MALE     | True   | New York    | h@gmail.com      |
        | 2          | gigi44   | yearly    | Gillian    | Laney      | FEMALE   | True   | California  | y@gmail.com      |
        | 3          | lion15   | friend1   | John       | Smith      | MALE     | False  | Texas       | hi@gmail.com     |
        | 4          | natedog  | nathan5   | Nathan     | Rocke      | UNKNOWN  | True   | Wisconsin   | you@yahoo.com    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer DataBase" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "username" to "Happy5"
    And I set the "password" to "12345"
    And I set the "first_name" to "Caitlyn"
    And I set the "last_name" to "Fuagzi"
    And I select "False" in the "active" dropdown
    And I select "Male" in the "gender" dropdown
    And I set the "address" to "North Dakota"
    And I set the "email" to "cait@gmail.com"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "username" field should be empty
    And the "password" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Happy5" in the "username" field
    And I should see "12345" in the "password" field
    And I should see "Caitlyn" in the "first_name" field
    And I should see "Fuagzi" in the "last_name" field
    And I should see "False" in the "active" dropdown
    And I should see "Male" in the "gender" dropdown
    And I should see "North Dakota" in the "address" field
    And I should see "cait@gmail.com" in the "email" field