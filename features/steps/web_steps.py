######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "customer_"


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when('I press the "View Details" button for the first customer')
def step_impl(context):
    button = WebDriverWait(context.driver, 10).until(
        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".view-details-btn"))
    )
    button.click()


@then("I should see all details for the customer in a modal")
def step_impl(context):
    WebDriverWait(context.driver, 10).until(
        expected_conditions.visibility_of_element_located((By.ID, "customerDetailsModal"))
    )
    modal = context.driver.find_element(By.ID, "customerDetailsModal")
    assert modal.is_displayed(), "Modal is not displayed"
    details = [
        "detail-username",
        "detail-first-name",
        "detail-last-name",
        "detail-email",
    ]
    for detail in details:
        assert (
            context.driver.find_element(By.ID, detail).text != ""
        ), f"{detail} is empty"


@when('I set the "customer_id" field to "{customer_id}"')
def step_impl(context, customer_id):
    input_field = context.driver.find_element(By.ID, 'customer_id')
    input_field.clear()
    input_field.send_keys(customer_id)

@when('I try to retrieve the customer with the ID "{customer_id}"')
def step_impl(context, customer_id):
    input_field = context.driver.find_element(By.ID, 'customer_id')
    input_field.clear()
    input_field.send_keys(customer_id)
    context.driver.find_element(By.ID, 'retrieve-btn').click()

@when('I delete the customer with ID "{customer_id}"')
def step_impl(context, customer_id):
    context.driver.find_element(By.ID, 'customer_id').send_keys(customer_id)
    context.driver.find_element(By.ID, 'delete-btn').click()

@when('I find the ID for "{username}" and delete the customer')
def step_impl(context, username):
    context.driver.find_element(By.ID, 'list-btn').click()
    try:
        WebDriverWait(context.driver, 20).until(
            expected_conditions.presence_of_element_located((By.ID, 'search_results'))
        )
        print("Search results are visible.")
    except TimeoutException:
        print("Failed to find the search results within the timeout period.")
        raise
    
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#search_results tr")
    print(f"Found {len(rows)} rows in search results.")
    customer_id = None
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[1].text == username:
            customer_id = cells[0].text
            break
    if customer_id:
        context.driver.find_element(By.ID, 'customer_id').send_keys(customer_id)
        context.driver.find_element(By.ID, 'delete-btn').click()
    else:
        raise Exception(f"Customer with username {username} not found")
    
@when(u'I press the "Activate" button for customer "{username}"')
def step_impl(context, username):
    customer_row = WebDriverWait(context.driver, 10).until(
        expected_conditions.visibility_of_element_located((By.XPATH, f"//td[text()='{username}']/.."))
    )
    activate_button = customer_row.find_element(By.CSS_SELECTOR, ".activate-btn")
    activate_button.click()

@when(u'I press the "Deactivate" button for customer "{username}"')
def step_impl(context, username):
    customer_row = WebDriverWait(context.driver, 10).until(
        expected_conditions.visibility_of_element_located((By.XPATH, f"//td[text()='{username}']/.."))
    )
    deactivate_button = customer_row.find_element(By.CSS_SELECTOR, ".deactivate-btn")
    deactivate_button.click()
