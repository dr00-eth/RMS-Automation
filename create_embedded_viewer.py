import os
import json

def create_embedded_viewer(bookings_folder, template_file, output_file):
    # Read the HTML template
    with open(template_file, 'r') as f:
        template = f.read()

    # Gather booking data
    booking_data = {}
    for filename in os.listdir(bookings_folder):
        if filename.endswith('.html'):
            reservation_id = filename.split('.')[0]
            with open(os.path.join(bookings_folder, filename), 'r') as f:
                booking_data[reservation_id] = f.read()

    # Convert booking data to JSON
    json_data = json.dumps(booking_data)

    # Insert the JavaScript data into the template
    output_html = template.replace('/*BOOKING_DATA*/{}/*BOOKING_DATA*/', json_data)

    # Write the final HTML file
    with open(output_file, 'w') as f:
        f.write(output_html)

    print(f"Created embedded viewer: {output_file}")

# Call this function in your main script
create_embedded_viewer('cr_bookings', 'booking-viewer-template.html', 'cr-booking-viewer.html')