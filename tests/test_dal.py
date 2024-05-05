import unittest
from datetime import date
import pprint
import dal


class TestDAL(unittest.TestCase):
    def test_is_site_available_for_date(self):
        site_id = 'P1'
        start_night = '2024-09-12'
        last_night = '2024-09-12'
        result = dal.MyDB().is_site_available_for_date(site_id, start_night, last_night)
        self.assertTrue(result)

        site_id = 'P1'
        start_night = '2024-05-12'
        last_night = '2024-05-12'
        result = dal.MyDB().is_site_available_for_date(site_id, start_night, last_night)
        self.assertFalse(result)

    def test_is_site_occupancy_fit(self):
        site_id = 'P1'
        occupancy = 2
        result = dal.MyDB().is_site_occupancy_fit(site_id, occupancy)
        self.assertTrue(result)

        site_id = 'P1'
        occupancy = 10
        result = dal.MyDB().is_site_occupancy_fit(site_id, occupancy)
        self.assertFalse(result)

    def test_add_booking(self):
        site_id = 'P1'
        customer_id = 241
        booking_date = date.fromisoformat('2024-08-01')
        nights = 1
        occupancy = 2
        result = dal.MyDB().add_booking(customer_id, site_id, booking_date, nights, occupancy)
        self.assertEqual(result, 1)

    def test_list_all_customers(self):
        customers = dal.MyDB().list_all_customers()
        self.assertGreater(len(customers), 10)

    def test_smart_search_customer(self):
        search_keyword = "02"
        customers = dal.MyDB().smart_search_customer(search_keyword)
        self.assertGreater(len(customers), 4)
        # TODO: more scenarios should be tested here
        # pprint.pp(customers)

if __name__ == '__main__':
    unittest.main()
