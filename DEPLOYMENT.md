# SkinScan Deployment Guide

This guide covers deploying the SkinScan full-stack application to production.
- **Backend**: Deployed via Docker Compose (FastAPI + Caddy auto-SSL) on an AWS EC2 instance.
- **Frontend**: Deployed to Vercel.

## 1. AWS EC2 Setup (Backend)

1. **Launch Instance**:
   - Go to AWS EC2 Console > Launch Instance.
   - Choose **Ubuntu 24.04 LTS (ARM64)** AMI.
   - Instance Type: `t4g.small`.
   - Key Pair: Create a new one or use an existing one to SSH.
   - Storage: 20GB gp3.

2. **Security Group**:
   - Create a new Security Group with the following inbound rules:
     - **SSH (22)**: Restrict source to **My IP** (highly recommended) or your team's IPs.
     - **HTTP (80)**: Anywhere (0.0.0.0/0).
     - **HTTPS (443)**: Anywhere (0.0.0.0/0).

3. **Elastic IP**:
   - Go to Elastic IPs in the EC2 dashboard.
   - Allocate a new Elastic IP.
   - Associate it with your newly created `t4g.small` instance.

## 2. DNS Configuration

Assuming your root domain is `skinscan.in`.

1. Go to your domain registrar's DNS settings.
2. **Backend**: Add an `A` record for `api.skinscan.in` pointing to the **Elastic IP** you allocated above.
3. **Frontend (later)**: Vercel will provide `CNAME` or `A` records to point your root domain (`skinscan.in`) and `www` to their servers.

*(Wait 5-10 minutes for the `api.` A record to propagate before proceeding with backend deployment to ensure Caddy can provision SSL).*

## 3. Backend Deployment

1. **SSH into the instance**:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@<YOUR_ELASTIC_IP>
   ```

2. **Run the One-Time Setup Script**:
   Copy the `scripts/setup-ec2.sh` script to the server, or curl it if your repo is public. If private, you can manually clone the repo using a deploy key, then run:
   ```bash
   sudo bash backend/scripts/setup-ec2.sh
   ```
   *This installs Docker, creates a `skinscan` user, and prepares the environment.*

3. **Configure Environment Variables**:
   Switch to the application user and edit the config:
   ```bash
   su - skinscan
   cd ~/skincare/backend
   nano .env
   ```
   Fill in all the production values (use `.env.example` as a reference):
   - `APP_ENV=production`
   - `FRONTEND_ORIGIN=https://skinscan.in`
   - `DOMAIN=api.skinscan.in`
   - **Crucial**: Ensure `DATABASE_URL` (Neon), `GEMINI_API_KEY`, and `JWT_SECRET` are correctly set.

4. **Deploy**:
   ```bash
   bash scripts/deploy.sh
   ```
   *This pulls the latest code, builds the Docker image, runs Alembic migrations, starts the API and Caddy, and waits for a healthy response.*

5. **Verify**:
   Visit `https://api.skinscan.in/healthz` in your browser. It should show `{"status": "ok", "db": "connected"}`.

## 4. Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel.
2. Select the `/frontend` directory as the Root Directory.
3. **Framework Preset**: Next.js.
4. **Build Command**: `npm run build`.
5. **Environment Variables**:
   Add the following (from your `.env.local.example`):
   - `NEXT_PUBLIC_API_BASE_URL`: `https://api.skinscan.in/api/v1`
   - `NEXT_PUBLIC_TURNSTILE_SITE_KEY`: (Your Cloudflare Turnstile Site Key)
6. Click **Deploy**.
7. Once deployed, go to the Vercel project **Settings > Domains** and add your custom domain (`skinscan.in`). Follow Vercel's instructions to configure the DNS records.

## 5. Third-Party Integrations Checklist

- [ ] **Cloudflare Turnstile**: Ensure `skinscan.in` (and `localhost` for dev) is added to your Turnstile widget settings in the Cloudflare dashboard.
- [ ] **Google Cloud Console**: If you are using Google OAuth later, register `https://api.skinscan.in/api/v1/auth/google/callback` as an Authorized Redirect URI.
- [ ] **Resend**: Ensure your sending domain (e.g., `skinscan.in`) is verified in the Resend dashboard.
- [ ] **AWS S3 / Cloudflare R2**: Ensure the bucket is created and the IAM user / API token has read/write permissions if you enabled photo storage.

## 6. Pre-Launch Smoke Test Checklist

Once everything is deployed, test the following flow on a real mobile device:
1. **Load**: Go to `https://skinscan.in`. Check that the UI loads smoothly and is mobile-responsive.
2. **Consent**: Check both checkboxes on the landing screen.
3. **Capture**: Grant camera permissions, take a selfie (or upload from gallery).
4. **Email**: Enter your email address. Verify the Turnstile CAPTCHA passes.
5. **Analysis**: Wait for the scanning animation. Ensure it successfully transitions to the Report screen.
6. **Email Delivery**: Check your inbox for the beautifully formatted HTML report from Resend.
7. **Rate Limiting**: Try to scan a few more times with the same email to ensure the rate limiter (e.g., limit of 3) successfully triggers and blocks the request with a friendly error.
8. **Deletion**: Call the deletion API (via a test script or Swagger UI at `/docs` if enabled) to ensure your account, DB rows, and S3 photos are cleanly deleted.
