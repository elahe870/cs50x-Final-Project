# cs50x-Final-Project: GMP (Good Manufacturing Practice)

Purpose:    
    A secure, digital platform designed for inspectors in the food and pharmaceutical industries to efficiently record, manage, and review inspection reports.

Motivation:
    Addressing the industry's need in developing countries for reliable and efficient inspection systems.

Impact:
    This project can serve as a starting point for developing digital solutions in the field of inspection and compliance.

Features: 
    📄 All form fields are dynamically defined, making it easy to create and customize new forms.

    📷 Allows capturing photo using the camera or uploading saved image for each inspection.

    📝 Completed inspections can be saved as PDF documents.

Future Improvements:

    🔐 Implement admin authentication to enable administrative control over user roles and permissions (User Management).

    📊 Add advanced search and reporting features to the inspections, forms library, and added user management sections.

Installation Tips:

    -Ensure `cs50` and `pdfkit` are installed via pip: 
        pip install cs50 pdfkit

    - wkhtmltopdf should be installed (on 1-windows or 2-linux , recognized in program) in 
    order to pdf files generate successfully.

    - SQLite is used for local database storage (no additional setup needed).


The database (GMP.db) includes the following tables:

users: stores user information (id, username, hash, role, created_at)

forms: defines inspection form templates (id, name, description, created_by)

form_fields: defines fields within each form (id, form_id, label, field_type, options, required, display_order)

inspections: stores individual inspection reports (id, form_id, inspector_id, submitted_at, location, notes, score)

inspection_fields: stores user responses to each field (id, inspection_id, field_id, value, comment)

inspection_images: stores image filenames related to inspections (id, inspection_id, filename, uploaded_at)

