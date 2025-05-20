# GMP (Good Manufacturing Practice)

#### Video Demo:  https://youtu.be/NE3dVVWyKnE
    This video demo shows some part of the program : shows briefly the Form Library navbar section. which defines forms with completely dynamic fields. (These fields can have "text", "textarea" "dropdown", "radio", "checkbox", "number", "date" type but because of time not shown in video). Then in video I try to fill in a new inspection in one of the form's format. in this part I can capture photo or upload a photo file and they are shown and saved. Then I save this inspection to a PDF file in a chosen sub-directory in pdf_exports directory. Photos attached to this inspection will be included in PDF.

#### Description:
     This project is a starting point to create a secure, digital platform designed for inspectors in the food and      pharmaceutical industries to design forms dynamically and efficiently record, manage, and review inspection reports.


#### Project address in github: 
    https://github.com/elahe870/cs50x-Final-Project


## 💊CS50x-Final-Project: GMP (Good Manufacturing Practice)

### Purpose:    

    A secure, digital platform designed for inspectors in the food and pharmaceutical industries to efficiently record,     manage, and review inspection reports.

### Motivation:

    Addressing the industry's need in developing countries for reliable and efficient inspection systems.

### Impact:

    This project can serve as a starting point for developing digital solutions in the field of inspection and compliance.

### Features: 

    📄 All form fields are dynamically defined, making it easy to create and customize new forms.

    📷 Allows capturing photo using the camera or uploading saved image for each inspection.

    📝 Completed inspections can be saved as PDF documents.

### Installation Tips:

    - Ensure `cs50` and `pdfkit` are installed via pip: 
        pip install cs50 pdfkit

    - SQLite is used for local database storage (no additional setup needed).

    - 📄 PDF Generation Requirement: Installing wkhtmltopdf
        To enable PDF generation in this application, ensure that wkhtmltopdf is installed and accessible. The application automatically checks both Windows and Linux path for wkhtmltopdf.

        For Windows:
            1- Download the Windows installer from the official wkhtmltopdf downloads page.

            2- Run the installer and follow the on-screen instructions to complete the installation.

            3- Verify the installation by opening Command Prompt and running: wkhtmltopdf --version
               You should see the installed version number displayed.

        For Linux:
            1- sudo apt install wkhtmltopdf
            
            2- Verify the installation by opening Command Prompt and running: wkhtmltopdf --version
               You should see the installed version number displayed.
               
        Note: Ensure that the wkhtmltopdf executable is in your system's PATH so that the application can access it.

        By following these steps, you'll have wkhtmltopdf properly installed, allowing the application to 
        generate PDF files successfully.


### The database (GMP.db) includes the following tables:

    users: stores user information (id, username, hash, role, created_at)

    forms: defines inspection form templates (id, name, description, created_by)

    form_fields: defines fields within each form (id, form_id, label, field_type, options, required, display_order)

    inspections: stores individual inspection reports (id, form_id, inspector_id, submitted_at, location, notes, score)

    inspection_fields: stores user responses to each field (id, inspection_id, field_id, value, comment)

    inspection_images: stores image filenames related to inspections (id, inspection_id, filename, uploaded_at)

    📝Note: The file `db_schema_safe.txt` contains all the `CREATE TABLE` statements needed to set up the database.
    

### Future Improvements:

    🔐 Implement admin authentication to enable administrative control over user roles and permissions (User Management).

    📊 Add advanced search and reporting features to the inspections, forms library, and added user management sections.

### Acknowledgements

During the development of this project, I used the following tools to assist with ideas, design, implementation, and debugging:

- **ChatGPT** – for help with understanding concepts, generating code snippets, and improving design structure.
- **GitHub Copilot** – for code suggestions and auto-completion while programming.
- **Perplexity AI** – for gathering information and exploring ideas during the planning and research phase.

These tools were used to support learning and accelerate development, while ensuring that I understood and implemented all parts of the project myself in accordance with CS50’s academic honesty policy.

### Contact Information:

    es.haghighat95@gmail.com
    github and edx username: elahe870

