# GoPlan: GitHub, Render and AWS runbook

This version stays Django-only: Django serves the pages and JSON APIs, SQLite works locally, and a managed PostgreSQL database is the recommended production database. Do not commit `.env`, `db.sqlite3`, API keys, or cloud credentials.

## 1. Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # Windows: copy .env.example .env
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Plan a road or metro route, then open **Trip history** in the shared menu.

## 2. Push the complete project to GitHub

Create an empty repository on GitHub first. From this project folder:

```bash
git init
git branch -M main
git add .
git commit -m "Modernize GoPlan Django application"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If the remote already exists:

```bash
git remote -v
git add .
git commit -m "Update GoPlan navigation and trip history"
git push
```

Before pushing, check:

```bash
git status
git check-ignore .env db.sqlite3
```

## 3. Deploy the Django app on Render

1. In Render, choose **New → Web Service**, connect the GitHub repository, and select the `main` branch.
2. Use:
   - **Environment:** Python 3
   - **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start command:** `gunicorn IntelligentMap.wsgi:application`
3. Add environment variables in Render (not in GitHub):

```text
DJANGO_SECRET_KEY=<long-random-secret>
DEBUG=False
ALLOWED_HOSTS=your-service.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-service.onrender.com
# Add this after creating a Render Postgres database:
DATABASE_URL=<Render internal PostgreSQL connection string>
```

Add `ORS_API_KEY` only if you use that provider. Keep the existing public OpenStreetMap/Open-Meteo fallbacks subject to their usage policies.

Render Free web services sleep after inactivity and have an ephemeral filesystem. That means local SQLite and uploaded files can disappear after restart/deploy. Use PostgreSQL for `TripRecord` data and object storage for user uploads before calling this production-ready.

## 4. Production database options

### Recommended: PostgreSQL

The included settings already switch from SQLite to PostgreSQL when `DATABASE_URL` exists. Add the Render Postgres internal connection string as `DATABASE_URL`; the dependency and driver are already in `requirements.txt`. A managed Render Postgres database is the shortest learning path; a free database can have expiry/limits, so check its current plan before relying on it.

### AWS RDS PostgreSQL

Use RDS when you need a longer-lived AWS setup. It is not the cheapest student prototype because the database instance can incur charges, needs backups/security-group setup, and should not be publicly exposed. Store the `DATABASE_URL` or separate database variables in Render Secrets.

### AWS S3 for files, not relational records

S3 is object storage: use it for photos, exported itineraries, and other files. Store route/user metadata in PostgreSQL. Create a private bucket, enable Block Public Access, enable default encryption, and give the app an IAM role/user limited to that bucket. Never put AWS access keys in GitHub.

For Django uploads, add `django-storages` and `boto3`, then configure `STORAGES["default"]` with `storages.backends.s3.S3Storage`. For this current dataset-heavy app, keep bundled static images in the repository initially; move only user-generated media to S3 when that feature exists.

## 5. Student/free-cost answer

An education email does not automatically make every AWS or Render resource free. AWS Educate currently advertises free hands-on labs and AWS has advertised a student credit grant; AWS Free Tier and promotional credits are account-, service-, region-, and time-dependent. Verify the offer in the AWS Educate/Free Tier console before creating billable resources. AWS S3 is pay-as-you-go, so set a billing alarm and a budget.

Render offers free web services for testing/hobby use, but its free filesystem is ephemeral and free Postgres has plan limitations/expiry. For a student project, the safest low-cost path is:

1. Render Free web service for the Django app.
2. A small managed PostgreSQL option with a current free/hobby plan, or Render Postgres only for a temporary demo.
3. S3 only after you need uploads, with a budget alarm.

## 6. What to add next

- User accounts and ownership rules before sharing trip history between devices.
- PostgreSQL and a migration/backup policy before public launch.
- A privacy page explaining location use, route-provider requests and deletion.
- Rate limiting and authentication on write APIs.
- A server-side cache for geocoding, weather and route calls.
- Automated tests for route saving, trip isolation, language direction, and mobile navigation.
- A background job for heavy translation model loading if native-language traffic grows.
- Error monitoring, structured logs, uptime checks and a custom domain.