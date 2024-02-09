# Freelance Marketplace App

## Overview

The Skill Marketplace App is a web application that connects sellers offering various skills and services with customers looking to hire someone to complete a job. This app was built using Flask in Python. 

Sellers can sign up for an account, create a profile showcasing their skills and experience, and list the types of services they offer. Customers can browse seller profiles and listings and connect with sellers to get quotes and hire the right person for the job.

Some key features include:

- Seller accounts and profiles
- Service listings and search/browse 
- Customer accounts
- Request for quotes and seller messaging
- Booking and payments system
- Review and rating system

## Installation

To install and run this Flask application locally:

1. Clone this repo
```
git clone https://github.com/Andrewtanui/freelance.git
```

2. Navigate into the project directory
```
cd freelance
```

3. Create a virtual environment and activate it
```
python3 -m venv venv
source venv/bin/activate
```

4. Install the requirements
```
pip install -r requirements.txt
```

5. Set the FLASK_APP environment variable
```
export FLASK_APP=app
```

6. Run the application
```
flask run
```

The app will be served at http://localhost:5000/ by default.

## Usage

The Skill Marketplace App has two main types of users - sellers and customers. Sellers can create an account, build their profile, add service listings, and manage booking requests. Customers can browse and search for sellers, get quotes, and request bookings.

### Seller Accounts

Sellers first need to create an account. This will allow them to log in and create/manage their profile and service listings.

To create an account, navigate to the signup page and enter your information.

Once registered, sellers can create their profile by adding details like:
- Profile photo
- Bio 
- Service area
- Skills/qualifications
- Certifications
- Insurance documentation
- Availability
- Past work examples

### Service Listings

In addition to their profile, sellers need to create service listings detailing the types of services they offer. This is how customers will find and connect with them.

Listings should include:
- Service category and subcategories
- Service name/title 
- Description of service
- Pricing/rates
- Photos
- FAQ

Sellers can create multiple listings to advertise all their service offerings.

### Customer Accounts

Customers can browse and search seller profiles and listings without creating an account. However, to request quotes or book services, they need to register and log in.

This allows the app to keep track of their bookings and allow secure payments.

### Booking Services

Once logged in, customers can message sellers to get quotes and availability. If they want to move forward with a booking, they can select the date/time on the seller's calendar and pay the quoted price.

The seller will then receive a notification of the new booking request. They can confirm or decline the booking.

## Payments

Payment will just be an example for now.

## Reviews & Ratings

After completing a service, customers are prompted to leave a review and rating for the seller.

This helps build seller profiles and reputation. Ratings are displayed prominently on seller profile pages.

## Developer Notes

Some additional notes for developers working on this project:

- The app uses a PostgreSQL database. See `models.py` for schema details.
- S3 is used to store profile images and listing photos.
- Flask-Login is used for authentication. See `auth.py`.
- Flask-WTForms is used for forms and validation. See `forms.py`.
- The app configuration is set via the config.py file.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
