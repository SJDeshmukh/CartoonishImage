import psycopg2
import base64

# Function to get the database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='dpg-ctnuipdsvqrc73b4c260-a.frankfurt-postgres.render.com',
            database='cartoondatabase',
            user='cartoondatabase_user',
            password='VeniS20ArXFHvmN3L1xLCDL1yE8vn2E6'
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# Function to extract base64 image data, decode it and save as an image
def extract_and_convert_image(image_id):
    # Get the database connection
    conn = get_db_connection()

    if conn is None:
        return
    
    cursor = conn.cursor()

    try:
        # Fetch the base64 image data, name, and email based on the provided image ID
        cursor.execute("SELECT name, email, image FROM users WHERE id = %s", (image_id,))  # Adjust table name if needed
        result = cursor.fetchone()

        if result:
            image_data_base64 = result[2]  # Extract the base64 image data from the query result

            # Decode the base64 string to get image data
            image_data = base64.b64decode(image_data_base64)

            # Write the decoded image data to a file
            with open(f"output_image_{image_id}.jpg", "wb") as image_file:
                image_file.write(image_data)

            print(f"Image has been saved as 'output_image_{image_id}.jpg'")

        else:
            print(f"No image found for ID {image_id}")

    except Exception as e:
        print(f"Error extracting and saving image: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

# Call the function with a specific ID (e.g., ID = 5)
extract_and_convert_image(11)
