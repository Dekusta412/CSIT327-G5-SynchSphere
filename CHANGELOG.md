Version 1.0.0 — Initial Release

🚀 Overview



This is the first working version of SynchSphere, a time synchronization and notification system designed to manage international meetings efficiently across different time zones.



🧩 Features Implemented



Django Project Setup



Initialized Django project and virtual environment (env).



Configured Supabase as the main database backend.



Added environment variable handling using .env.



User Authentication System



Added accounts app for login and registration.



Implemented Django UserCreationForm and AuthenticationForm.



Added custom email uniqueness validation in registration.



Username validation automatically handled by Django.



Added secure password validation with Django’s built-in validators.



Created redirects for successful login/logout.



UI and Styling



Integrated TailwindCSS via CDN (no npm build required).



Designed modern, dark-themed, glassy Login and Register pages.



Styled and displayed all form field validation errors (red messages, highlights).



Project Structure



Organized templates under /templates/accounts/.



Added templatetags/form\_tags.py for custom as\_widget filter.



Configured settings.py with DIRS = \[BASE\_DIR / "templates"] for clean template loading.



Version Control



Initialized local Git repository.



Added .gitignore (excludes env/, .env, node\_modules/, etc.).



Connected and pushed project to GitHub:

https://github.com/Dekusta412/CSIT327-G5-SynchSphere.git



Added requirements.txt for reproducible setup.



Prepared .env.example for future collaborators.



🔧 Developer Setup Notes



To set up locally after cloning:



git clone https://github.com/Dekusta412/CSIT327-G5-SynchSphere.git

cd SynchSphere

python -m venv env

.\\env\\Scripts\\activate

pip install -r requirements.txt

python manage.py runserver

