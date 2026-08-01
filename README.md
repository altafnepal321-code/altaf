# School EMIS with Streamlit and Supabase

This project is a school management information system built with Python, Streamlit, and Supabase.

## Features
- Register students
- View student list
- Mark daily attendance
- Record fee payments

## Setup
1. Create a Supabase project.
2. Run the SQL from [supabase_schema.sql](supabase_schema.sql) in the Supabase SQL editor.
3. Copy [.env.example](.env.example) to `.env` and fill in your credentials.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   streamlit run app.py
   ```

## Environment Variables
- SUPABASE_URL
- SUPABASE_KEY

The application uses Supabase as its only database. Configure both environment variables before starting the app.

## Roles
- Admin: create teacher and accountant accounts, and add courses.
- Teacher: record attendance.
- Accountant: manage fees and add, update, or delete students.
- Principal: view all school and transaction records without edit controls.
- Student: view profile, results, fee status, and library records.
- Librarian: manage books, issue and return books, fines, and bill downloads.

Librarian accounts can be created from the signup page.
