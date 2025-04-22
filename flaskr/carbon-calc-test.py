
def calculations_carbon_page():
            # Collect inputs from the form
            home_size = 1200
            heating_type = 1.53
            
            num_appliances = 10
            num_laptops = 2
            num_desktops = 1
            
            has_car = ""
            car_travel_5_miles = 20
            car_travel_10_miles = 10
            
            uses_train = ""
            train_travel_count = 8
            train_long_journeys = False
            
            
            # Corrected carbon emission factors (kg CO₂ per unit)
            heating_factors = {
                "Gas": 1.53,  # kg CO₂ per ft²
                "Oil": 2.2,
                "Wood": 0.8,
            }
            appliance_factor = 50  # kg per appliance
            laptop_factor = 30  # kg per laptop
            desktop_factor = 50  # kg per desktop

            car_5_miles_factor = 0.4  # kg per trip
            car_10_miles_factor = 0.8  # kg per trip
            train_short_factor = 0.1  # kg per trip
            train_long_factor = 0.3  # kg per trip
            bus_short_factor = 0.2  # kg per trip
            bus_long_factor = 0.5  # kg per trip

            # Calculate total carbon usage for a year
            total_carbon = 0
            # home
            home_carbon = home_size * 1.53
            appliance_carbon = num_appliances * appliance_factor
            # appliances
            laptop_carbon = num_laptops * laptop_factor
            desktop_carbon = num_desktops * desktop_factor
            # transport
            car_5_carbon = car_travel_5_miles * car_5_miles_factor   # Adjusted to monthly trips
            
            car_10_carbon = car_travel_10_miles * car_10_miles_factor   # Adjusted to monthly trips
            
            train_carbon = train_travel_count *  train_short_factor # per year
            

            # Convert total carbon usage to metric tons
            total_carbon =( home_carbon + appliance_carbon + laptop_carbon + desktop_carbon + car_5_carbon + car_10_carbon + train_carbon )*12
            total_carbon = total_carbon / 1000  # Convert kg to tons
            total_carbon_use = total_carbon

            # Redirect to results page with calculated carbon usage
            print(f"Home Size: {home_carbon}")
            print(f"Number of Appliances: {appliance_carbon}")
            print(f"Number of Laptops: {laptop_carbon}")
            print(f"Number of Desktops: {desktop_carbon}")
            print(f"Car Travel 5 Miles: {car_5_carbon}")
            print(f"Car Travel 10 Miles: {car_10_carbon}")
            print(f"Train Travel Count: {train_carbon}")
            print(f"Train Long Journeys: {total_carbon_use}")
    
            # Call the function to execute the calculations and print the results
calculations_carbon_page()
