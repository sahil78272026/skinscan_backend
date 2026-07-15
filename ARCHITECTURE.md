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
*   **Razorpay (Payments & Paywall):**
    *   **Connection:** Manages the premium subscription flow. The backend securely creates payment orders and verifies webhook signatures to upgrade users. The system enforces a strict 3-scan limit for free users before triggering the Razorpay flow.
*   **Google OAuth (Authentication):**
    *   **Connection:** Integrated directly into the Next.js frontend using `@react-oauth/google` for frictionless login, securely trading Google credentials for a JWT managed by the backend.

---

## 6. Internal Business Logic & Compliance
*   **Medical Term Sanitization:** The AI prompt strictly forbids medical terminology (like "acne" or "melasma") to comply with App Store and legal requirements. Any edge cases are caught by a backend sanitizer mapping medical terms to cosmetic equivalents (e.g., "blemishes", "uneven tone").
*   **Dynamic Product Recommendation Engine:** The backend maps the user's top cosmetic concerns to an internal database of 60+ real-world Ayurvedic/Himalayan products. It dynamically generates robust **Google Shopping URLs** for each product and pairs them with high-quality **Unsplash** category images, ensuring the UI always displays live, purchasable products with zero broken links.

---

## Summary of the User Flow
1. User visits `skinscan.fit` (Served by **Vercel** via **Cloudflare**).
2. User takes a selfie. The frontend checks if they have consumed their 3 free scans. If yes, the **Razorpay** paywall is triggered.
3. If allowed, the user authorizes via **Google OAuth** or Email. **Cloudflare Turnstile** generates a token for email flows.
4. Frontend sends the photo, credentials, and token to `api.skinscan.fit` (**AWS EC2**).
5. **Caddy** receives the request securely, decrypts the HTTPS, and hands it to **FastAPI**.
6. FastAPI authenticates the user and updates the scan count in **Neon Postgres**.
7. FastAPI sends the photo to **Google Gemini** for analysis with strict cosmetic-only prompt instructions.
8. (Optional) FastAPI saves the photo to **Cloudflare R2** if consent was provided.
9. FastAPI sanitizes the output and injects curated **Product Recommendations** with dynamic live-shopping links.
10. FastAPI formats the analysis and sends it to the user via **Resend** (if requested).
11. FastAPI returns the structured analysis data back to the Frontend, which displays the interactive, premium UI report.
