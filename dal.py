"""
Data Access Layer

All database accessing logic is handled here.
It assumes all input parameters have been validated and are valid.

"""

import mysql.connector
from datetime import timedelta, datetime
import config
from scgexceptions import ExceptionViolatedBusinessLogic

global db_connection
global db_cursor

class MyDB:
    def __init__(self):
        self.conn = None
        self.cursor = None

        self.conn = mysql.connector.connect(
            user=config.dbuser,
            password=config.dbpass, host=config.dbhost,
            database=config.dbname, autocommit=True)
        self.conn.time_zone = config.DB_TIMEZONE

        self.cursor = self.conn.cursor(prepared=True, dictionary=True)

    def list_campers_for_a_date(self, camp_date):
        sql = """
            SELECT s.site_id as site_id, c.firstname as first_name, c.familyname as family_name, 
                c.email as email, c.phone as phone, b.occupancy as occupancy 
            FROM sites s JOIN bookings b ON s.site_id = b.site
                JOIN customers c ON b.customer = c.customer_id
            WHERE b.booking_date = %s
            ORDER BY s.site_id ASC, c.familyname ASC;
        """
        self.cursor.execute(
            sql,
            (camp_date,))
        camper_list = self.cursor.fetchall()
        return camper_list

    def search_available_sites(self, occupancy, first_night, last_night):
        sql = """
            SELECT sites.site_id as site_id, sites.occupancy as occupancy
            FROM sites 
            WHERE occupancy >= %s AND site_id NOT IN 
                (SELECT site
                FROM bookings
                WHERE booking_date between %s AND %s);
        """

        self.cursor.execute(
            sql,
            (occupancy, first_night, last_night))
        available_sites = self.cursor.fetchall()
        return available_sites

    def list_all_customers(self):
        sql = """
            SELECT * FROM customers ORDER BY customer_id DESC;
        """

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def add_booking(self, customer_id, site_id, booking_date, nights, occupancy):
        error_messages = []
        if not self.is_customer_id_exist(customer_id):
            error_messages.append("Customer Id does not exist: " + customer_id)
            raise ExceptionViolatedBusinessLogic(error_messages)

        first_night = booking_date
        last_night = first_night + timedelta(days=int(nights))
        if not self.is_site_available_for_date(site_id, first_night, last_night):
            error_messages.append("Site(%s) is not available between %s and %s" % (site_id, first_night, last_night))
            raise ExceptionViolatedBusinessLogic(error_messages)

        if not self.is_site_occupancy_fit(site_id, occupancy):
            error_messages.append("Site(%s) does not have occupancy of %d" % (site_id, occupancy))
            raise ExceptionViolatedBusinessLogic(error_messages)

        sql = """
            INSERT INTO bookings (site, customer, booking_date, occupancy)
            VALUES (%s, %s, %s, %s)
        """

        params = []
        for i in range(nights):
            params.append((site_id, customer_id, booking_date, occupancy))
            booking_date += timedelta(days=int(1))

        self.cursor.executemany(sql, params)
        if self.cursor.rowcount <= 0:
            error_messages.append(
                "Somehow adding booking failed. Site: %s, customer: %s, booking_date: %s, occupancy: %s"
                % (site_id, customer_id, booking_date, occupancy))
            raise ExceptionViolatedBusinessLogic(error_messages)

    def is_customer_id_exist(self, customer_id):
        sql = """
            SELECT count(*) as count
            FROM customers
            WHERE customer_id = %(customer_id)s;
        """
        params = {
            'customer_id': customer_id
        }
        self.cursor.execute(sql, params)
        result = self.cursor.fetchone()
        return True if result['count'] > 0 else False

    def is_site_available_for_date(self, site_id, start_night, last_night):
        sql = """
            SELECT count(*) as count
            FROM bookings
            WHERE site = %(site_id)s AND (booking_date BETWEEN %(start_night)s AND %(last_night)s);
        """
        params = {
            'site_id': site_id,
            'start_night': start_night,
            'last_night': last_night
        }
        self.cursor.execute(sql, params)
        result = self.cursor.fetchone()
        return False if result['count'] > 0 else True

    def is_site_occupancy_fit(self, site_id, occupancy):
        sql = """
            SELECT count(*) as count
            FROM sites
            WHERE site_id = %(site_id)s AND occupancy >= %(occupancy)s;
        """
        params = {
            'site_id': site_id,
            'occupancy': occupancy
        }
        self.cursor.execute(sql, params)
        result = self.cursor.fetchone()
        return True if result['count'] > 0 else False

    def smart_search_customer(self, search_keyword):
        sql = """
            SELECT *
            FROM customers
            WHERE firstname LIKE %(search_keyword)s
            OR familyname LIKE %(search_keyword)s
            OR phone LIKE %(search_keyword)s
            OR email LIKE %(search_keyword)s;
        """
        # TODO: I think it's wrong that it can be used in this way. What if the search_keyword contains a "%" character
        #   in situations that it's valid. It loses the meaning of having parameters automatically being escaped to
        #   avoid SQL injection. A deep dive of how prepared statement works in Python Mysql lib's required.
        params = {
            'search_keyword': "%" + search_keyword + "%"
        }
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def get_customer_by_id(self, customer_id):
        sql = """
            SELECT * FROM customers WHERE customer_id = %(customer_id)s;
        """
        params = {
            'customer_id': customer_id
        }
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def update_customer(self, customer):
        # customer dict
        error_messages = []
        sql = """
            UPDATE customers
            SET firstname = %(firstname)s, familyname = %(familyname)s, phone = %(phone)s, email = %(email)s
            WHERE customer_id = %(customer_id)s;
        """
        params = customer
        self.cursor.execute(sql, params)
        if self.cursor.rowcount <= 0:
            error_messages.append("Update customer info failed")
            raise ExceptionViolatedBusinessLogic(error_messages)

    def add_customer(self, customer):
        error_messages = []
        sql = """
            INSERT INTO customers (firstname, familyname, phone, email)
            VALUES (%(firstname)s, %(familyname)s, %(phone)s, %(email)s)
        """
        params = customer
        self.cursor.execute(sql, params)
        if self.cursor.rowcount <= 0:
            error_messages.append("Add customer failed")
            raise ExceptionViolatedBusinessLogic(error_messages)

    def count_customer_bookings(self, customer_id, current_date, count_type):
        # default to all
        compare_date_condition = ''
        if count_type == 'current':
            compare_date_condition = r' AND booking_date = %(current_date)s'
        elif count_type == 'future':
            compare_date_condition = r' AND booking_date > %(current_date)s'
        elif count_type == 'past':
            compare_date_condition = r' AND booking_date < %(current_date)s'

        sql = """
            SELECT count(*) as nights, ROUND(AVG(occupancy)) as avg_occupancy
            FROM bookings
            WHERE customer = %(customer_id)s
                
        """ + compare_date_condition + ';'

        params = {
            'customer_id': customer_id,
            'current_date': current_date
        }
        self.cursor.execute(sql, params)
        result = self.cursor.fetchone()
        return {
            'nights': result['nights'],
            'avg_occupancy': result['avg_occupancy']
        }
