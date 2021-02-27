API specification: 
* BASE URL: https://sample-disjoin1.herokuapp.com/api/
* ENDPOINTS: 
1. geofence_stores:
    - GET: 
        {
          "center": [lat, lng],
          "radius": number
        }

2. userLogin:
    - POST:
      {
        "email": string,
        "password": string
      }

3. users:
    - POST:
      {
        "id":  string,
        "first_name": string,
        "last_name": string,
        "email": string,
        "username": string,
        "password": string,
        "street": string,
        "city": string,
        "state": string,
        "pincode": string,
        "isActive": true,
        "addedDate": number
      }
    
    - DELETE:
      {
        "id": string
      }

4. Stores:
    - POST:
      {
        "sid": number,
        "sName": string,
        "username": string,
        "password": string,
        "streetName": string,
        "city": string,
        "state": string,
        "zipcode": string,
        "timestampUTC": string,
        "isActive": true
      }
