# PLAB — General Overview

PLAB (P Lab / بي لاب) is a bilingual (English / Arabic) Django web application that connects a medical laboratory with its patients. The site provides:

- Patient accounts and secure access to lab test results
- Staff-managed records, publishing workflow for results and announcements
- Blog posts and public health advice
- Internationalized UI with RTL support for Arabic

Core user flows

- Administrators use the Django admin to manage users (patients), lab results (PDF uploads), posts, and announcements.
- Patients sign up or log in using their phone number and password, and view/download results on their dashboard when results are published.

Content and process highlights

- Results are uploaded and marked in the admin; only published results with associated files are visible to patients.
- Announcements are authored in the admin and shown on the home page.
- Blog posts support detail pages with canonical URLs and basic SEO metadata.

Documentation and where to look

- Technical and developer instructions: [README_TECHNICAL.md](README_TECHNICAL.md)
- Deployment commands and checklist: [DEPLOY.md](DEPLOY.md)
- Project configuration: `plab_project/settings.py`

Quick local run (development)

```bash
cd plab_project
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env      # edit as needed
python manage.py migrate
python manage.py compilemessages -l ar
python manage.py runserver
```

Support and contact

- For urgent issues or deployment assistance, open an issue in the repository or contact the project maintainer.
