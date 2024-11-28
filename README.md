# Vehicle-Store-Database
Pitt MSIS INFSCI 2710 - Database Management Systems Final Project Design Document


### Introduction/Abstract

- Simplifying vehicle search and management for renters and buyers. Explore, list, and analyze vehicle sale and rental listings with ease. 
- By providing a comprehensive and user-friendly platform, we empower users to effortlessly navigate the often complex and time-consuming process of finding and managing vehicle listings. Whether it's assisting renters in finding their dream vehicle or helping buyers identify their future vehicle, our app streamlines the entire journey. 



### E-R Model
![ER diagram](https://github.com/user-attachments/assets/dc106c31-cca6-4d01-b3e8-7b0cc3bb5746)





### Business rules

| **Entity 1**  | **Entity 2**   | **Cardinality on Entity 1 side** | **Cardinality on Entity 2 side** | **Business Rule(s)**                                         |
| ------------- | -------------- | -------------------------------- | -------------------------------- | ------------------------------------------------------------ |
| User          | UserType       | m                                | n                                | A user can have multiple roles, and a role can apply to multiple users. |
| User          | Password       | 1                                | 1                                | Each user has a single password for security purposes and to avoid ambiguity. |
| User          | Review         | 1                                | m                                | Each user can leave multiple reviews, but a review belongs to one user only. |
| User          | Vehicle        | 1                                | m                                | Each user can own or rent multiple vehicles, but a vehicle is associated with only one user at a time. |
| User          | Booking        | 1                                | m                                | Our system allows each user to create multiple bookings, but each booking belongs to one user only. |
| Vehicle       | Booking        | 1                                | m                                | Each vehicle can be part of multiple bookings, but a booking involves only one vehicle. |
| Vehicle       | Review         | 1                                | m                                | Our system allows each vehicle to have multiple reviews. But a review can only belong to one vehicle. |
| Vehicle       | VehicleDetail  | 1                                | 1                                | Each vehicle must have detailed information (e.g., make, model, year, VIN#, color). Our system allows each vehicle to have only one detail, to avoid ambiguity. |
| Vehicle       | MarketListings | 1                                | 1                                | Our system allows each vehicle to have only one MarketListings, to avoid ambiguity. |
| Vehicle       | Contract       | 1                                | m                                | Our system allows each vehicle belong to multiple contracts. But a contract can only contain one vehicle. |
| Vehicle       | Image          | 1                                | 1                                | Our system allows each vehicle to have only one image, to avoid ambiguity. |
| ZipCode       | Address        | 1                                | m                                | Each zip code corresponds to multiple addresses, but each address is part of only one zip code |
| City          | Address        | 1                                | m                                | Each city has multiple addresses, but each address belongs to only one city. |
| State         | City           | 1                                | m                                | Each state contains multiple cities, but each city belongs to only one state. |
| Contract	| User	    	 | 1	  			    | m	                               | Each user can have multiple contracts, but a contract belongs to one user only. |
| Contract	| Vehicle	 | 1	  			    | m	                               | Each vehicle can belong to multiple contracts, but a contract is associated with only one vehicle.|
| Payment       | Contract       | 1                                | m                                | Our system allows each payment to be used by multiple contracts. But a contract can only have one payment. |
| PaymentMethod | Payment        | 1                                | m                                | Our system allows each payment method to be used by multiple payments. But a payment can only have one payment method. |


### DDL Statment
![DDL Statement 1](https://github.com/user-attachments/assets/671fd6ed-a52e-4172-9ad3-8ce91fc8cf8c)

![DDL Statement 2](https://github.com/user-attachments/assets/e07cf6dc-fd8a-433e-8eb5-84784b999737)

### Front-end Design
The "<form>" element is used to connect the front-end to the back-end, specifying the destination path and method via action and method.

### Front-end and Back-end Interactions

#### Basic elements:
#### Flask backend logic routing
Flask's @app.route defines the backend logic that receives, processes, and returns request results.

#### Template engine (Jinja2):
Flask's render_template dynamically renders HTML pages, passing in variables such as error_message.

#### Flask redirect function
Use Flask's redirect function to realize the page jump.

### How it works:
When a user accesses the system's page, the Flask backend processes the request through routing and returns the HTML page to the user's browser using render_template, containing form elements (such as input boxes, checkboxes, buttons, etc.).

Once the user sees the page in their browser, they submit the form information by filling out the form and clicking the submit button. After the original form element defined in the html to realize the interaction with the request.form in the route of flask.

Through method=“POST” to realize the HTTP POST request to send the completed form to the route of flask.

On the backend, Flask receives the POST request and gets the form data submitted by the user through request.form.

If the form data submitted by the user is to be stored, the backend will validate the data (e.g., check if the required fields are empty).
If the data is validated, the backend will use the database connection library (pymysql) to connect to the MySQL database, and then insert the form data into the database through SQL statements.

The backend will return a response when the insertion operation is complete. If the insertion is successful, the backend redirects the user to a new page. If the insertion fails, the backend returns an error message and can display the appropriate error message on the page.

If the data on the form is to be validated, for example, user login. Then if the CAPTCHA validation passes, the backend will continue with the username and password validation.

The backend verifies that the user name and password provided by the user are correct by querying the database for the user information (using pymysql to connect to the database and execute the SQL query). 

If the validation is successful, the backend stores the user's login status in the session and redirects to the appropriate user dashboard page based on the type of user.

If username or password validation fails, the backend will re-render the login page via render_template with an error message indicating that the username or password entered by the user is invalid. The user can then re-fill the form according to the error message and submit again.



### Additional Notes

