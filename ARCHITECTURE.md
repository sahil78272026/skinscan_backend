# SkinScan Platform Architecture & Infrastructure

This document provides an extensive overview of all the technologies, third-party services, and tools used in the SkinScan platform, detailing exactly how they connect and interact to deliver a seamless, production-ready experience.

---

## 1. Domain & DNS Routing
The flow of internet traffic begins with the domain name and is managed entirely by Cloudflare for security and performance.

*   **Namecheap (Domain Registrar):** The domain (`skinscan.fit`) was purchased here. Namecheap's only role is to point the domain's Nameservers to Cloudflare.
*   **Cloudflare (DNS & Edge Security):** Acts as the central traffic director. 
    *   **Frontend Routing:** The root domain (`skinscan.fit`) and `www` subdomain use CNAME/A records pointing to Vercel's global network. Cloudflare Proxies this traffic (Orange Cloud) for DDoS protection.
    *   **Backend Routing:** The `api.skinscan.fit` subdomain uses an A record pointing directly to the AWS EC2 Elastic IP. This is set to "DNS Only" (Gray Cloud) to allow the backend server to generate its own SSL certificates natively.

---

## 2. Frontend Infrastructure
*   **Framework:** Next.js (React) using Tailwind CSS and Framer Motion for micro-animations.
*   **Hosting (Vercel):** The frontend is deployed as a serverless web application on Vercel. 
*   **Connection to Backend:** The frontend communicates with the backend exclusively via the `NEXT_PUBLIC_API_BASE_URL` environment variable (e.g., `https://api.skinscan.fit/api/v1`).
*   **Cloudflare Turnstile (CAPTCHA):** Embedded on the frontend to prevent bots. The frontend uses a public "Site Key" to generate a secure token when the user enters their email. This token is sent to the backend for validation.

---

## 3. Backend Infrastructure & Web Server
*   **Framework:** FastAPI (Python), utilizing Pydantic for strict data validation and SQLAlchemy for database interactions.
*   **Server Hosting (AWS EC2):** 
    *   **Instance:** A `t4g.small` (ARM64 architecture) instance running Ubuntu 24.04 LTS.
    *   **Networking:** An Elastic IP is attached to the instance to ensure the IP address never changes upon restart. An AWS Security Group acts as a firewall, allowing public access only on ports 80 (HTTP) and 443 (HTTPS), and restricting SSH (Port 22) access.
*   **Containerization (Docker & Docker Compose):** The entire backend runs inside isolated Docker containers, ensuring the environment is identical to local development.
*   **Reverse Proxy & SSL (Caddy):** Caddy runs in its own Docker container alongside the FastAPI container. It listens on ports 80 and 443, automatically requests and renews free SSL certificates from Let's Encrypt for `api.skinscan.fit`, and securely routes traffic to the FastAPI application running internally on port 8000.

---

## 4. Database Layer
*   **Provider:** Neon (Serverless Postgres).
*   **Connection:** The backend connects to Neon securely via a `DATABASE_URL` connection string.
*   **Usage:** Stores user data (emails), analysis metadata, and opt-in preferences. Alembic is used within the backend container to automatically run database schema migrations upon deployment.

---

## 5. Third-Party Integrations (The "Brain" & Utilities)
The FastAPI backend acts as an orchestrator, securely communicating with several external APIs using secret keys stored in the `.env` file.

*   **Google Gemini (AI Engine):** 
    *   **Model:** `gemini-2.5-flash`.
    *   **Connection:** The backend sends the user's selfie and a strict system prompt to Google's API. Gemini returns a structured JSON payload containing the detected skin concerns and recommended routines.
*   **Cloudflare Turnstile (Verification API):** 
    *   **Connection:** When the frontend sends the user's email and CAPTCHA token to the backend, the backend makes a secure API call to `challenges.cloudflare.com` using a "Secret Key" to verify the token is legitimate before saving the email to the database.
*   **Resend (Email Delivery):** 
    *   **Connection:** After the AI analysis is complete, the backend dynamically generates an HTML email report and sends it to Resend via their API.
    *   **Domain Verification:** Resend is authorized to send emails "from" `reports@skinscan.fit` because specific verification TXT/MX records were added to the Cloudflare DNS settings.
*   **Cloudflare R2 (Object Storage):** 
    *   **Connection:** Used as an AWS S3-compatible storage bucket. If a user explicitly "opts-in" to photo storage, the backend uploads the selfie to the R2 bucket using `boto3` and AWS-style access keys, keeping the heavy image files out of the Neon database.

---

## Summary of the User Flow
1. User visits `skinscan.fit` (Served by **Vercel** via **Cloudflare**).
2. User takes a selfie and enters their email. **Cloudflare Turnstile** generates a token.
3. Frontend sends the photo, email, and token to `api.skinscan.fit` (**AWS EC2**).
4. **Caddy** receives the request securely, decrypts the HTTPS, and hands it to **FastAPI**.
5. FastAPI verifies the token with **Cloudflare Turnstile**.
6. FastAPI saves the user to **Neon Postgres**.
7. FastAPI sends the photo to **Google Gemini** for analysis.
8. (Optional) FastAPI saves the photo to **Cloudflare R2**.
9. FastAPI formats the Gemini analysis and sends it to the user via **Resend**.
10. FastAPI returns the structured analysis data back to the Frontend, which displays the interactive report.
