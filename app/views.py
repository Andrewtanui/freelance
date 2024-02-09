from app import app
from flask import render_template

@app.route('/')
def home():
  return render_template('index.html')





  """_summary_
    The function takes user inputs.
    1. User Role: This is a drop-down list where users can select their roles i.e., Customer or Seller.
    2. Full Name: A text box for full name of the user.
    3. Email ID: An email id as unique identifier for user.
    4. Password: A password field so that user can enter their password.
    5. Confirm Password: So that user can confirm their password. Both passwords should be same.
    6. Phone Number: A field to take phone number of the user.
    7. Address: Text area to provide address details.
    8. Country: Drop down menu with countries listed.
    9. City: Autocomplete city field.
    10. Postal Code: Zip code of the location.
    
    
  Returns:
  
    If all fields are filled correctly it will show a success message otherwise error messages according to the wrong input.
    - If all fields are filled correctly it will show a success message "Your account has been created successfully." else it shows error messages if any field is left empty or both passwords don't match - If all fields are filled correctly it will show a success message on the web page else it shows - If all fields are filled correctly it will show a success message otherwise error messages according to the wrong - If all fields are filled correctly it will show a success message "Your account has been created successfully".
    
    If the email or phone number already exists. Flash error message "Email Id / Phone Number Already Exists" will appear. - If all fields are filled correctly it will show a success message "Your account has been created successfully".
    
  """
