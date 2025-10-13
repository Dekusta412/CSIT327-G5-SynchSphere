# 🌐 SynchSphere

### **A Time Synchronization and Notification Platform**

SynchSphere is a web-based system designed to automatically adjust and synchronize meeting times across multiple time zones. It eliminates confusion from manual time conversions, ensuring users never miss important meetings or activities.  
By combining real-time notifications with intelligent time zone management, SynchSphere enhances coordination and efficiency for international teams, students, and organizations.

---

## 🧰 Tech Stack

**Frontend**
- Tailwind CSS (via CDN)
- HTML5 / Django Templates

**Backend**
- Django (Python)
- Supabase (PostgreSQL database)
- Python-dotenv for environment management

**Other Tools**
- Git & GitHub (version control)
- PowerShell / VS Code (development)
- Gmail SMTP (for email notifications & password resets) (Work-in-progress, just set the DEBUG=True for now)

---

## ⚙️ Setup & Run Instructions

Follow these steps to run the project locally:

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Dekusta412/CSIT327-G5-SynchSphere.git
cd CSIT327-G5-SynchSphere
```

### 2️⃣ Create and activate a virtual environment
``` bash
python -m venv env
.\env\Scripts\activate
```

### 3️⃣ Install dependencies
``` bash
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables

Create a .env file in your project root and configure:
``` bash
SECRET_KEY=django-insecure-k*ql75^#ih$j65!qnjp)9v218rjg=0#xni9$&0a60cof%&z9=a
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://postgres.lbrxusakyibimejwlgpj:Yj91$7okue1DHKp@aws-1-us-east-1.pooler.supabase.com:5432/postgres

EMAIL_USER=synchsphere.noreply@gmail.com
EMAIL_PASS=lacsrtpihixdxhp
```

### 5️⃣ Run the development server
``` bash
python manage.py runserver
```

| Name               | Role                     | CIT-U Email                                                   |
| ------------------ | ------------------------ | ------------------------------------------------------------- |
| Dexter Dela Riarte | Lead Developer | [dexter.delariarte@cit.edu](mailto:dexter.delariarte@cit.edu) |
| Jon Nicole F. Din  | Frontend Developer  | [jonnicole.din@cit.edu](mailto:jonnicole.din@cit.edu) |
| James Stefan C. Legaspino  | Backend Developer  | [jamesstefan.legaspino@cit.edu](mailto:jamesstefan.legaspino@cit.edu) |


## 🚀 Deployed Link
Deployment in progress – available soon








