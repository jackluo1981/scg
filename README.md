# SCG Report

## Web application design
- Three tiers architecture. Data Access Layer, Business Logic Layer and Presentation Layer
    - Logically clear
    - Collaboration
    - Testing
    - Maintenance
    - Scaling
- Modules explain:
    - dal.py: Data Access Layer. All DB interactions happen here
    - bll.py: Business Logic Layer.
        - Validating input data
        - Calling data access layer to fulfill functionalities, then data required by presentation layer will be populated
    - app.py: controller and flask app.
        - Serving http responses and controlling flows.
        - Collecting inputs from presentation layer, calling business logic layer to populate data required for\
            the presentation layer, then rendering HTML with data's being passed in.
    - templates folder. All HTML templates used for rendering HTML(presentation layer) are stored here
    - helpers.py: helpers functions like general validation functions
    - scgexceptions.py: Custom exception classes
    - config.py: global configuration like db parameters
    - tests folder: unit test files
- http request methods
    - GET: query
    - POST: add
    - PUT: update
    - DELETE: delete
    - Because HTML form only supports GET and POST, so an extra parameter "mode={add||update}" has been used for POST requests
- Validations
    - Front end validation in forms
    - Server side validation in Business Logic Layer
    - Controller simply passes input from presentation layer to business logic layer, but any errors will be captured\
        , then being passed back to presentation layer to advise users gracefully
    - Regex has been widely used in validations
- Timezone has been considered. Ideally, UTC time should be used for data persistence, then being converted to(and from)\
    local time in presentation layer to provide better usability. It requires proper handling of time/datetime throughout the application.\
    A practical way with reasonable effort is to keep timezone as New Zealand time everywhere in the application including
    the database.
- Navigation and flow of user interaction
    - Intuitive
    - Staying on the form and inputted fields retained if it fails validations or any errors occurred
