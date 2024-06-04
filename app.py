from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime

from mysql.connector.cursor import MySQLCursorDict

import bll
from scgexceptions import ExceptionInvalidParameters, ExceptionViolatedBusinessLogic
import mysql.connector

print('### starting server')

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/campers", methods=['GET'])
def campers():
    camp_date = request.args.get('camp_date')
    camper_list = None
    error_message = None

    if not camp_date:
        # no camp_data at all, it's fine. User might just land on the page
        camp_date = str(datetime.now().date())

    # all good, then retrieve the data
    try:
        camper_list = bll.list_campers_for_a_date(camp_date)
        if not camper_list:
            error_message = "No bookings for the date: " + camp_date
    except ExceptionInvalidParameters as e:
        error_message = str(e)

    # camp_date = "2024-06-02"
    return render_template("camperlist.html", camp_date=camp_date, camper_list=camper_list,
                           error_message=error_message)


@app.route("/booking", methods=['GET', 'POST'])
def booking():
    if request.method == "GET":
        return render_template("booking_search_available_sites.html",
                               booking_date=datetime.now().date(),
                               booking_nights=1,
                               occupancy=1)
    else:
        # search for available campsites for a date
        first_night = request.form.get('booking_date')
        nights = request.form.get('booking_nights')
        occupancy = request.form.get('occupancy')

        error_messages = []
        if first_night and nights and occupancy:
            try:
                available_sites = bll.search_available_sites(occupancy, first_night, nights)
                if available_sites:
                    customer_list = bll.list_all_customers()
                    return render_template("booking_form.html",
                                           booking_date=first_night,
                                           booking_nights=nights,
                                           occupancy=occupancy,
                                           customer_list=customer_list,
                                           site_list=available_sites)
                else:
                    error_messages.append("No available sites")
            except ExceptionInvalidParameters as e:
                error_messages = e.args[0]
        else:
            if not first_night:
                first_night = datetime.now().date()

            if not nights:
                nights = 1

            if not occupancy:
                occupancy = 1

        return render_template("booking_search_available_sites.html",
                               error_messages=error_messages,
                               booking_date=first_night,
                               booking_nights=nights,
                               occupancy=occupancy)


@app.route("/booking/add", methods=['POST'])
def make_booking():
    success_message = None
    error_messages = []
    booking_date = request.form.get('booking_date')
    nights = request.form.get('booking_nights')
    occupancy = request.form.get('occupancy')
    customer_id = request.form.get('customer_id')
    site_id = request.form.get('site_id')

    try:
        bll.add_booking(customer_id, site_id, booking_date, nights, occupancy)
    except ExceptionInvalidParameters as e:
        error_messages = e.args[0]
    except ExceptionViolatedBusinessLogic as e:
        error_messages = e.args[0]

    if not error_messages:
        success_message = "Booking has been added successfully."

    return render_template("booking_search_available_sites.html",
                           success_message=success_message,
                           error_messages=error_messages,
                           booking_date=datetime.now().date(),
                           booking_nights=1,
                           occupancy=1)


@app.route("/customers", methods=['GET'])
def list_customers():
    search_keyword = request.args.get('search_keyword')
    customers = bll.smart_search_customer(search_keyword)
    return render_template("customers.html",
                           customers=customers)


@app.route("/customer", methods=['GET', 'POST'])
def customer_info():
    if request.method == "GET":
        # render the form
        # mode from query string. mode = edit || add
        # form action: PUT || POST
        mode = request.args.get("mode")
        mode = mode if mode else "update"
        customer_id = request.args.get("customer_id")
        customer = bll.get_customer_by_id(customer_id)
        return render_template("customer_form.html",
                               mode=mode,
                               customer=customer)

    elif request.method == "POST":
        mode = request.form.get("mode")
        mode = mode if mode else "update"
        if mode == 'update':
            # update customer info
            success_message = None
            error_messages = []
            customer = request.form.to_dict()
            try:
                bll.update_customer(customer)
            except ExceptionInvalidParameters as e:
                error_messages = e.args[0]
            except ExceptionViolatedBusinessLogic as e:
                error_messages = e.args[0]

            if not error_messages:
                success_message = "Customer info has been updated successfully."

            return render_template("customer_form.html",
                                   success_message=success_message,
                                   error_messages=error_messages,
                                   mode='update',
                                   customer=customer)

        else:
            # add
            success_message = None
            error_messages = []
            customer = request.form.to_dict()
            try:
                bll.add_customer(customer)
            except ExceptionInvalidParameters as e:
                error_messages = e.args[0]
            except ExceptionViolatedBusinessLogic as e:
                error_messages = e.args[0]

            if not error_messages:
                success_message = "Customer has been added successfully."
                customer = None

            return render_template("customer_form.html",
                                   success_message=success_message,
                                   error_messages=error_messages,
                                   mode='add',
                                   customer=customer)


@app.route("/reports/customer-bookings", methods=['GET'])
def report_customer_bookings():
    error_messages = []
    customer_id = request.args.get('customer_id')
    report = None
    try:
        report = bll.report_customer_bookings(customer_id)
    except ExceptionViolatedBusinessLogic as e:
        error_messages = e.args[0]

    return render_template("report_customer_bookings.html",
                           error_messages=error_messages,
                           report=report)


if __name__ == '__main__':
    app.run()