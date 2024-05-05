"""
Business Logic Layer

It handles business logic, and invokes data access layer if needed.

Typically, business logic layer functions are being called from the control layer(routing in app.py).

Input parameters from the presentation layer(templates) are being passed to the business logic layer, validated, then

business logic is being applied and invoking data access layer to interact with the database if required, also

returned data is guaranteed valid.

"""

import dal
import helpers
from datetime import date, datetime
from datetime import timedelta
import re
import scgexceptions
from scgexceptions import ExceptionInvalidParameters, ExceptionViolatedBusinessLogic


def list_campers_for_a_date(camp_date):
    is_valid_date = helpers.is_valid_html_date_param(camp_date)
    if not is_valid_date:
        raise ExceptionInvalidParameters('Invalid date')

    return dal.MyDB().list_campers_for_a_date(camp_date)


def search_available_sites(occupancy, first_night, nights):
    error_messages = []
    try:
        occupancy = int(occupancy)
    except Exception as e:
        error_messages.append("Invalid occupancy")

    if occupancy < 1 or occupancy > 8:
        error_messages.append("Invalid occupancy")

    try:
        nights = int(nights)
    except Exception as e:
        error_messages.append("Invalid nights")

    if nights < 1 or nights > 5:
        error_messages.append("Invalid nights")

    if not helpers.is_valid_html_date_param(first_night):
        error_messages.append("Invalid Start Night")

    if error_messages:
        raise ExceptionInvalidParameters(error_messages)

    first_night = date.fromisoformat(first_night)
    last_night = first_night + timedelta(days=int(nights))
    return dal.MyDB().search_available_sites(occupancy, first_night, last_night)


def list_all_customers():
    return dal.MyDB().list_all_customers()


def add_booking(customer_id, site_id, booking_date, nights, occupancy):
    error_messages = []
    try:
        customer_id = int(customer_id)
    except Exception as e:
        error_messages.append("Invalid customer_id")

    site_id = str(site_id)

    if not helpers.is_valid_html_date_param(booking_date):
        error_messages.append("Invalid Booking Date")

    try:
        nights = int(nights)
    except Exception as e:
        error_messages.append("Invalid nights")

    if nights < 1 or nights > 5:
        error_messages.append("Invalid nights")

    try:
        occupancy = int(occupancy)
    except Exception as e:
        error_messages.append("Invalid occupancy")

    if occupancy < 1 or occupancy > 8:
        error_messages.append("Invalid occupancy")

    if error_messages:
        raise ExceptionInvalidParameters(error_messages)

    booking_date = date.fromisoformat(booking_date)
    try:
        dal.MyDB().add_booking(customer_id, site_id, booking_date, nights, occupancy)
    except scgexceptions.ExceptionViolatedBusinessLogic as e:
        raise e


def smart_search_customer(search_keyword):
    # whatever you have, I will take it
    if search_keyword:
        search_keyword = re.sub(r"\W", "", search_keyword)
        return dal.MyDB().smart_search_customer(search_keyword)
    else:
        return dal.MyDB().list_all_customers()


def get_customer_by_id(customer_id):
    return dal.MyDB().get_customer_by_id(customer_id)


def update_customer(customer):
    error_messages = validate_customer_for_update(customer)
    if error_messages:
        raise ExceptionInvalidParameters(error_messages)

    dal.MyDB().update_customer(customer)


def add_customer(customer):
    error_messages = validate_customer_for_add(customer)
    if error_messages:
        raise ExceptionInvalidParameters(error_messages)

    dal.MyDB().add_customer(customer)

def validate_customer_for_update(customer):
    error_messages = []

    if not customer['customer_id']:
        error_messages.append("No customer id")

    if ('firstname' not in customer) or (not helpers.is_valid_name(customer['firstname'])):
        error_messages.append("Invalid first name")

    if (('familyname' not in customer) or
            (customer['familyname'] and (not helpers.is_valid_name(customer['familyname'])))):
        error_messages.append("Invalid family name")

    if not customer['phone']:
        error_messages.append("No phone number")
    elif not helpers.is_valid_phone(customer['phone']):
        error_messages.append("Invalid phone number")

    if (('email' not in customer) or
            (customer['email'] and (not helpers.is_valid_email(customer['email'])))):
        error_messages.append("Invalid email")

    return error_messages


def validate_customer_for_add(customer):
    error_messages = []

    if not customer['firstname']:
        error_messages.append("No First Name")
    elif not helpers.is_valid_name(customer['firstname']):
        error_messages.append("Invalid first name")

    if (('familyname' not in customer)
            or (customer['familyname'] and (not helpers.is_valid_name(customer['familyname'])))):
        error_messages.append("Invalid family name")

    if not customer['phone']:
        error_messages.append("No phone number")
    elif not helpers.is_valid_phone(customer['phone']):
        error_messages.append("Invalid phone number")

    if (('email' not in customer)
            or (customer['email'] and (not helpers.is_valid_email(customer['email'])))):
        error_messages.append("Invalid email")

    return error_messages


def report_customer_bookings(customer_id):
    error_messages = []

    customer = dal.MyDB().get_customer_by_id(customer_id)
    if not customer:
        error_messages.append("Customer does not exist. Id: " + customer_id)
        raise ExceptionViolatedBusinessLogic(error_messages)

    current_date = datetime.now().date()
    all_bookings = dal.MyDB().count_customer_bookings(customer_id, current_date, 'all')
    past_bookings = dal.MyDB().count_customer_bookings(customer_id, current_date, 'past')
    current_bookings = dal.MyDB().count_customer_bookings(customer_id, current_date, 'current')
    future_bookings = dal.MyDB().count_customer_bookings(customer_id, current_date, 'future')

    full_name = customer['firstname']
    if customer['familyname']:
        full_name += ", " + customer['familyname']

    return {
        'run_at': str(current_date),
        'customer_id': customer_id,
        'full_name': full_name,
        'phone': customer['phone'],
        'email': customer['email'],
        'all_bookings': all_bookings,
        'past_bookings': past_bookings,
        'current_bookings': current_bookings,
        'future_bookings': future_bookings
    }
