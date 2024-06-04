# SCG Report

## Web application design
- Three tiers architecture. Data Access Layer, Business Logic Layer and Presentation Layer. 
      The main benefits of applying three tiers architecture:
    - Logically clear
    - Collaboration
    - Testing
    - Maintenance
    - Scaling
- Modules:
    - dal.py: Data Access Layer. All DB interactions happen here
    - bll.py: Business Logic Layer.
        - Validating input data
        - Calling data access layer to fulfill functionalities, then data required by presentation layer will be populated
    - app.py: controller and flask app.
        - Serving http responses and controlling flows.
        - Collecting inputs from presentation layer, calling business logic layer to populate data required for
           the presentation layer, then rendering HTML with data's being passed in.
    - templates folder. All HTML templates used for rendering HTML(presentation layer) are stored here
    - helpers.py: helpers functions like general validation functions
    - scgexceptions.py: Custom exception classes
    - config.py: global configuration like db parameters
    - tests folder: unit test files
- Routing and templates:
    - "/campers" with "GET" method routes to "camperlist.html" view: Listing campers
    - "/booking" with "GET" method routes to "booking_search_available_sites.html" view: Opening search available sites for(step 1/2 of making bookings)
    - "/booking" with "POST" method routes to "booking_form.html" view: Opening the booking form(step 2/2 of making bookings)
    - "/booking/add" with "POST" method: Adding booking then redirected back to 1/2 of making bookings process.
    - "/customers" with "GET" method routes to "customers.html" view: Listing all customers.
    - "/customers" with "GET" method and "search_keyword=keyword" query parameter: "Like" searching customer by firstname, familyname, phone or email
    - "/customer" with "GET" method and "mode=update" and "customer_id={id}" query parameters, routes to "customer_form.html" view: Showing customer details form.
    - "/customer" with "POST" method and "mode=update" and "customer_id={id}" post parameters: Update customer details then stays on the customer details page
    - "/customer" with "GET" method and "mode=add" query parameter routes to "customer_form.html" view: Showing add customer details form.
    - "/customer" with "POST" method and "mode=add" post parameter: Add new customer then stays on the creation form.
    
- http request methods
    - GET: query actions including listing campers, searching customers, querying reports etc.
    - POST: add actions including adding new customers.
    - PUT: update action including modifying customer profiles.
    - DELETE: delete data. There is requirements for deleting data in this project, if there's any, this request method will be used.
    - Because HTML form only supports GET and POST, so an extra parameter "mode={add||update}" has been used for POST requests to differentiate Add and Update actions.
- Validations
    - Server side validation is critical because any data submitted from front end may be tampered. It's implemented in the Business Logic Layer
    - Front end validation makes prompting invalid data input by users on the page possible, which provides better user experience.
          It's implemented in template files of presentation layer.
    - Controller simply passes input from presentation layer to business logic layer, but any errors will be captured
        , then being passed back to presentation layer to advise users gracefully
    - Regex has been widely used in validations
- Timezone has been considered. Ideally, all servers should be running with UTC, and UTC time should be used for data persistence, then being converted to(and from)
    local time in presentation layer to provide better usability. It requires proper handling of time/datetime throughout the application.
    A practical way with reasonable effort is to keep timezone as New Zealand time everywhere in the application including
    the database.
- Navigation and flow of user interaction
    - Intuitive
    - Staying on the form and inputted fields retained if it fails validations or any errors occurred

## Database questions:
1. What SQL statement creates the customer table and defines its fields/columns?
(Copy and paste the relevant lines of SQL.)
```sql
    CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(45) NULL,
  `familyname` VARCHAR(60) NOT NULL,
  `email` VARCHAR(255) NULL,
  `phone` VARCHAR(12) NULL,
  PRIMARY KEY (`customer_id`));
```
2. Which line of SQL code sets up the relationship between the customer and booking
tables?
```sql
  CONSTRAINT `customer`
    FOREIGN KEY (`customer`)
    REFERENCES `customers` (`customer_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
```
3. Which lines of SQL code insert details into the sites table?
```sql
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P1', '5');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P4', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P2', '3');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P5', '8');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P3', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U1', '6');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U2', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U3', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U4', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U5', '2');
```
4. Suppose that as part of an audit trail, the time and date a booking was added to the
database needed to be recorded. What fields/columns would you need to add to
which tables? Provide the table name, new column name and the data type. (Do not
implement this change in your app.)

```
Table name: bookings
New column name: added_timestamp
Data type: TIMESTAMP
Explaination: The timestamp contains both date and time, so one field is sufficient for auditing, and it's convinient for querying.
```

5. Suppose the ability for customers to make their own bookings was added. Describe
two different changes that would be needed to the data model to implement this.
(Do not implement these changes in your app.)
```

```
