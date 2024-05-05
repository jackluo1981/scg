import unittest
from datetime import date
import dal
import bll
import scgexceptions


class TestBLL(unittest.TestCase):
    def test_add_booking(self):
        site_id = 'P1'
        customer_id = 241
        booking_date = '2024-08-01'
        nights = 1
        occupancy = 2
        try:
            bll.add_booking(customer_id, site_id, booking_date, nights, occupancy)
        except scgexceptions.ExceptionInvalidParameters as e:
            self.fail('Invalid parameters: ' + e.args[0])
        except scgexceptions.ExceptionViolatedBusinessLogic as e:
            self.fail('ViolatedBusinessLogic: ' + e.args[0])


if __name__ == '__main__':
    unittest.main()

