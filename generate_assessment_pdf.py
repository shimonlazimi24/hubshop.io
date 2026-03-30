#!/usr/bin/env python3
"""Generate Frodo Technical Assessment PDF for developer proposal."""

from datetime import date

from fpdf import FPDF


class AssessmentPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(130, 130, 130)
            self.cell(
                0, 8, "Frodo - Technical Assessment & Development Scope", align="R"
            )
            self.ln(12)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 30, 30)
        self.ln(4)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(50, 100, 200)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def sub_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bold_text(self, text: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text: str, indent: int = 10):
        x = self.get_x()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(x + indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(0.5)

    def table_header(self, cols: list[tuple[str, int]]):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(45, 85, 180)
        self.set_text_color(255, 255, 255)
        for label, w in cols:
            self.cell(w, 7, f" {label}", border=1, fill=True)
        self.ln()

    def table_row(self, cols: list[tuple[str, int]], alt: bool = False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        if alt:
            self.set_fill_color(240, 244, 250)
        else:
            self.set_fill_color(255, 255, 255)
        for val, w in cols:
            self.cell(w, 6.5, f" {val}", border=1, fill=True)
        self.ln()

    def callout_box(self, text: str):
        self.set_fill_color(255, 248, 230)
        self.set_draw_color(220, 180, 60)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(80, 60, 10)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, self.w - self.l_margin - self.r_margin, 18, style="DF")
        self.set_xy(x + 4, y + 2)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5.5, text)
        self.set_y(y + 20)


def build_pdf() -> str:
    pdf = AssessmentPDF()
    pdf.alias_nb_pages()
    pdf.set_margin(20)

    # === COVER / TITLE PAGE ===
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 14, "Frodo", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(
        0, 10, "Unified TikTok SaaS Platform", align="C", new_x="LMARGIN", new_y="NEXT"
    )
    pdf.ln(10)
    pdf.set_draw_color(50, 100, 200)
    pdf.set_line_width(1)
    mid = pdf.w / 2
    pdf.line(mid - 40, pdf.get_y(), mid + 40, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Technical Assessment &", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "Development Scope", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        0,
        7,
        f"Prepared: {date.today().strftime('%B %d, %Y')}",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0, 7, "Classification: Confidential", align="C", new_x="LMARGIN", new_y="NEXT"
    )

    # === PAGE 2: PROJECT OVERVIEW ===
    pdf.add_page()
    pdf.section_title("1. Project Overview")
    pdf.body_text(
        "Frodo is a SaaS platform that unifies TikTok's fragmented ecosystem "
        "(Shop, Developer, Marketing, LIVE, Research) into a single dashboard for agencies and brands. "
        "It handles cross-platform authentication, token management, data synchronization, "
        "and analytics - enabling users to manage all TikTok operations from one workspace."
    )

    pdf.sub_title("Tech Stack")
    cols = [("Layer", 35), ("Technology", 135)]
    pdf.table_header(cols)
    rows = [
        ("Backend", "Python 3.12, FastAPI, SQLAlchemy async, Pydantic v2, Celery 5"),
        ("Database", "PostgreSQL 16 (multi-tenant, JSONB), Redis 7"),
        ("Frontend", "Next.js 15 (App Router), React 19, Tailwind v4, TypeScript"),
        ("Sidecar", "Node.js 20, Fastify - TikTok Shop HMAC signing proxy"),
        ("Infra", "Docker Compose (6 services: api, worker, beat, pg, redis, sdk)"),
    ]
    for i, (layer, tech) in enumerate(rows):
        pdf.table_row([(layer, 35), (tech, 135)], alt=i % 2 == 1)

    pdf.ln(4)
    pdf.sub_title("Codebase Scale")
    cols2 = [("Metric", 55), ("Count", 115)]
    pdf.table_header(cols2)
    scale_rows = [
        ("Backend Python files", "~205 files, 53 services, 220+ API endpoints"),
        ("Database models", "120 ORM entity classes across 18 model files"),
        ("Frontend pages", "70+ pages, 14 dashboard sections, 35 reusable components"),
        ("Background workers", "12 Celery modules, 55+ scheduled tasks"),
        ("Test suite", "879 tests (842 unit + 37 integration)"),
        ("Domain modules", "11 fully implemented business modules"),
    ]
    for i, (m, c) in enumerate(scale_rows):
        pdf.table_row([(m, 55), (c, 115)], alt=i % 2 == 1)

    # === REAL API STATUS ===
    pdf.add_page()
    pdf.section_title("2. TikTok API Integration Status")

    pdf.callout_box(
        "KEY FINDING: No part of the system has ever been tested against real TikTok API "
        "responses. All integration is mock-tested only."
    )
    pdf.ln(2)

    pdf.sub_title("What Exists (Built)")
    pdf.bullet("5 real HTTP clients with production TikTok URLs (httpx.AsyncClient)")
    pdf.bullet("SDK sidecar making real fetch() calls for HMAC-SHA256 signing")
    pdf.bullet("PlatformGateway with rate limiting, circuit breaker, and retry logic")
    pdf.bullet("Token Vault with AES-256-GCM encryption for credential storage")
    pdf.bullet(
        "OAuth flows for all 4 platforms (TikTok Shop, Developer, Marketing, Research)"
    )

    pdf.ln(2)
    pdf.sub_title("What Has NOT Been Done")
    pdf.bullet("No real API calls have ever been made to any TikTok endpoint")
    pdf.bullet("No sandbox or test account testing performed")
    pdf.bullet("No validation of actual TikTok response JSON structures")
    pdf.bullet("tests/e2e/ directory is empty - zero end-to-end tests")
    pdf.bullet("Unknown behavior for real-world rate limits, errors, and edge cases")

    pdf.ln(2)
    pdf.sub_title("Credential Status")
    cols4 = [
        ("Platform", 35),
        ("Credentials in .env", 45),
        ("App Registration", 50),
        ("Status", 40),
    ]
    pdf.table_header(cols4)
    cred_rows = [
        ("TikTok Shop", "Populated", "Required (5-15 day review)", "Not registered"),
        ("Developer", "Empty", "Required (3-7 day review)", "Not registered"),
        ("Marketing", "Empty", "Required (3-7 day review)", "Not registered"),
        ("Research", "Empty", "Restricted access", "Not registered"),
    ]
    for i, (p, c, r, s) in enumerate(cred_rows):
        pdf.table_row([(p, 35), (c, 45), (r, 50), (s, 40)], alt=i % 2 == 1)

    # === PAGE: DEPLOYMENT STATUS ===
    pdf.add_page()
    pdf.section_title("3. Current Deployment & Infrastructure")

    pdf.sub_title("What Exists")
    pdf.bullet(
        "docker-compose.yml with 6 services (api, celery-worker, celery-beat, postgres, redis, tiktok-shop-sdk)"
    )
    pdf.bullet("Backend Dockerfile (python:3.12-slim)")
    pdf.bullet("SDK sidecar Dockerfile (multi-stage Node.js 20-alpine build)")
    pdf.bullet(".env.example with all required environment variables documented")
    pdf.bullet("Health check endpoints on all services")

    pdf.ln(2)
    pdf.sub_title("What Does NOT Exist")
    pdf.bullet("No CI/CD pipeline (no GitHub Actions, Jenkins, or GitLab CI)")
    pdf.bullet(
        "No infrastructure-as-code (no Terraform, CloudFormation, or Kubernetes manifests)"
    )
    pdf.bullet("No cloud deployment configuration of any kind")
    pdf.bullet("No staging or production environment - local Docker Compose only")
    pdf.bullet("No monitoring, logging aggregation, or error tracking integration")
    pdf.bullet("No TLS/HTTPS configuration")
    pdf.bullet("No secrets management (currently .env file based)")

    # === PRODUCTION READINESS ===
    pdf.ln(4)
    pdf.section_title("4. Production Readiness Gap Analysis")
    pdf.body_text(
        "A 79-item production readiness checklist exists in the documentation (docs/handover/05-production-readiness.md). "
        "Currently 0 of 79 items are completed. Below is a summary by priority tier."
    )

    pdf.sub_title("Critical Items (14) - Required Before Any Production Traffic")
    pdf.bullet("DEBUG=false, secrets in a secrets manager (not .env files)")
    pdf.bullet("TikTok app credentials provisioned for all required platforms")
    pdf.bullet("Production OAuth redirect URIs registered with TikTok")
    pdf.bullet("PostgreSQL with automated backups and failover")
    pdf.bullet("Redis with AOF persistence")
    pdf.bullet("HTTPS/TLS enabled on all endpoints")
    pdf.bullet("Database migrations applied and verified")
    pdf.bullet("Celery Beat running as exactly one instance")
    pdf.bullet("Health endpoints operational")
    pdf.bullet("Security scan passing (bandit, pip audit)")
    pdf.bullet("Multi-tenant data isolation verified")
    pdf.bullet("Token vault encryption active with backed-up keys")

    pdf.ln(2)
    pdf.sub_title("High Priority Items (17) - Should Have Before Launch")
    pdf.bullet("Error tracking integration (e.g., Sentry)")
    pdf.bullet("Structured logging to aggregation service")
    pdf.bullet("Alerting on API failures, error rates, queue depth")
    pdf.bullet("Database connection pooling (PgBouncer or equivalent)")
    pdf.bullet("E2E test suite (currently 0 tests)")
    pdf.bullet("Load testing (target: 50 concurrent workspaces)")
    pdf.bullet("Zero-downtime deployment procedure")
    pdf.bullet("Rollback procedure tested")
    pdf.bullet("JWT secret rotation procedure")
    pdf.bullet("All 20 Celery beat schedules verified with real data")
    pdf.bullet("Webhook signature verification tested with real payloads")

    pdf.ln(2)
    pdf.sub_title("Medium Priority Items (15) - Post-Launch Improvements")
    pdf.bullet("Read replicas for analytics queries")
    pdf.bullet("Frontend bundle optimization and CDN deployment")
    pdf.bullet("Billing integration (Stripe or equivalent)")
    pdf.bullet("Penetration testing")
    pdf.bullet("Data retention and cleanup jobs")
    pdf.bullet("Frontend component tests")

    # === DEVELOPMENT SCOPE ===
    pdf.add_page()
    pdf.section_title("5. Development Scope - What Needs To Be Built")

    pdf.sub_title("A. Validate Existing Code Against Real TikTok APIs")
    pdf.body_text(
        "The most critical unknown: does the existing code correctly handle real TikTok API responses? "
        "All 11 modules are built against documented API specs, but actual responses may differ. "
        "This requires connecting real credentials and testing each integration path."
    )
    pdf.bullet(
        "Register TikTok apps on all required portals (Shop, Developer, Marketing)"
    )
    pdf.bullet("Deploy a staging environment with real credentials")
    pdf.bullet("Test core flow: Register -> Connect Shop -> View Orders")
    pdf.bullet("Identify and fix any response parsing mismatches")
    pdf.bullet("Validate OAuth token refresh cycles work end-to-end")

    pdf.ln(2)
    pdf.sub_title("B. End-to-End Test Suite")
    pdf.body_text(
        "The tests/e2e/ directory is empty. A Playwright-based E2E test suite is needed to validate "
        "critical user journeys through the full stack (frontend -> backend -> TikTok APIs)."
    )

    pdf.ln(2)
    pdf.sub_title("C. CI/CD Pipeline")
    pdf.body_text(
        "No CI/CD exists. Needs: automated test runs on PR, lint/format checks, "
        "build verification, and deployment automation to staging/production."
    )

    pdf.ln(2)
    pdf.sub_title("D. Cloud Infrastructure & Deployment")
    pdf.body_text(
        "No cloud deployment exists. Needs infrastructure-as-code (Terraform or equivalent) for:"
    )
    pdf.bullet(
        "Staging environment (Docker Compose on VM or container service is acceptable)"
    )
    pdf.bullet(
        "Production environment (managed PostgreSQL, managed Redis, container orchestration)"
    )
    pdf.bullet("TLS/HTTPS termination")
    pdf.bullet(
        "Secrets management (AWS Secrets Manager, HashiCorp Vault, or equivalent)"
    )
    pdf.bullet(
        "Log aggregation and monitoring (Sentry, CloudWatch, Datadog, or equivalent)"
    )

    pdf.ln(2)
    pdf.sub_title("E. Production Hardening")
    pdf.body_text(
        "Address the 79-item production readiness checklist. Key areas: security hardening, "
        "database backup/failover, monitoring and alerting, rate limit tuning, "
        "and zero-downtime deployment procedures."
    )

    pdf.ln(2)
    pdf.sub_title("F. Billing Integration")
    pdf.body_text(
        "No billing or subscription management exists. "
        "If this is a paid SaaS product, Stripe (or equivalent) integration is needed for "
        "plan management, usage tracking, and payment processing."
    )

    # === TikTok APP REGISTRATION ===
    pdf.add_page()
    pdf.section_title("6. TikTok App Registration (Non-Development Dependency)")

    pdf.callout_box(
        "CRITICAL PATH: TikTok app registration requires manual submission and review. "
        "This should start immediately as it runs in parallel with development work."
    )
    pdf.ln(2)

    pdf.body_text(
        "The codebase expects TikTok API credentials to be provided via environment variables. "
        "These credentials come from registering applications on TikTok's developer portals. "
        "This is a manual, business-side process that involves:"
    )
    pdf.bullet("Creating developer accounts on each TikTok platform portal")
    pdf.bullet("Submitting app registration with required business documentation")
    pdf.bullet("Configuring OAuth redirect URIs for your deployment domain")
    pdf.bullet("Waiting for TikTok's review and approval")
    pdf.bullet("Receiving API credentials (app key, app secret) for each platform")

    pdf.ln(2)
    cols5 = [("Platform", 35), ("Registration Portal", 65), ("Required For", 70)]
    pdf.table_header(cols5)
    reg_rows = [
        (
            "TikTok Shop",
            "TikTok Shop Partner Center",
            "Commerce, orders, products, fulfillment",
        ),
        ("Developer", "TikTok for Developers", "Content, video publishing, login"),
        ("Marketing", "TikTok Marketing API", "Ads, creators, messaging, organic"),
        (
            "Research",
            "TikTok Research API",
            "Intelligence, trends, competitor tracking",
        ),
    ]
    for i, (p, portal, req) in enumerate(reg_rows):
        pdf.table_row([(p, 35), (portal, 65), (req, 70)], alt=i % 2 == 1)

    pdf.ln(4)
    pdf.body_text(
        "Note: The Research API has restricted access and may require additional approval. "
        "The platform functions without it - the Intelligence module would be the only affected area."
    )

    # === RECOMMENDED APPROACH ===
    pdf.add_page()
    pdf.section_title("7. Recommended Staging Approach")
    pdf.body_text(
        "Before investing in full production infrastructure, a lightweight staging deployment "
        "is recommended to validate the core integration with real TikTok APIs."
    )
    pdf.ln(2)
    pdf.sub_title("Staging Environment (Recommended)")
    pdf.bullet(
        "Single cloud VM or container service (e.g., AWS EC2, DigitalOcean Droplet)"
    )
    pdf.bullet("Docker Compose deployment (same as local dev - already works)")
    pdf.bullet("Containerized PostgreSQL and Redis (acceptable for staging)")
    pdf.bullet("Real TikTok API credentials configured")
    pdf.bullet("Goal: validate Register -> Connect Shop -> View Orders flow")

    pdf.ln(2)
    pdf.sub_title("Production Environment (After Staging Validation)")
    pdf.bullet("Managed PostgreSQL (e.g., AWS RDS with Multi-AZ and automated backups)")
    pdf.bullet("Managed Redis (e.g., AWS ElastiCache with AOF persistence)")
    pdf.bullet("Container orchestration (ECS, Fargate, or Kubernetes)")
    pdf.bullet("Frontend on CDN (Vercel or CloudFront + S3)")
    pdf.bullet("Full monitoring, alerting, and secrets management stack")

    # === SUMMARY TABLE ===
    pdf.add_page()
    pdf.section_title("8. Summary: What Is Built vs. What Is Needed")

    pdf.sub_title("Already Built (No Development Needed)")
    pdf.bullet("All 11 business domain modules with full API integration logic")
    pdf.bullet("Authentication system (JWT, OAuth, 5-tier RBAC, social login)")
    pdf.bullet("Token vault with AES-256-GCM encryption")
    pdf.bullet("Background task system (Celery + 55 scheduled tasks)")
    pdf.bullet("Frontend application (70+ pages, 14 dashboard sections)")
    pdf.bullet("TikTok Shop SDK sidecar (HMAC signing proxy)")
    pdf.bullet("879 unit and integration tests")
    pdf.bullet("Docker Compose setup for local development")

    pdf.ln(4)
    pdf.sub_title("Requires Development")
    cols6 = [("Work Item", 80), ("Category", 45), ("Notes", 45)]
    pdf.table_header(cols6)
    dev_rows = [
        ("Real TikTok API validation & fixes", "Integration", "Highest priority"),
        ("E2E test suite (Playwright)", "Testing", "Currently 0 tests"),
        ("CI/CD pipeline (GitHub Actions)", "DevOps", "None exists"),
        ("Cloud infrastructure (Terraform/IaC)", "DevOps", "None exists"),
        ("Monitoring & error tracking", "DevOps", "Sentry, logging"),
        ("TLS/HTTPS & secrets management", "Security", "Currently .env only"),
        ("Production readiness (79 items)", "Hardening", "0/79 completed"),
        ("Billing integration (Stripe)", "Feature", "If paid SaaS"),
    ]
    for i, (item, cat, notes) in enumerate(dev_rows):
        pdf.table_row([(item, 80), (cat, 45), (notes, 45)], alt=i % 2 == 1)

    pdf.ln(4)
    pdf.sub_title("Requires Ops / Business (Not Code)")
    cols7 = [("Task", 90), ("Owner", 40), ("Notes", 40)]
    pdf.table_header(cols7)
    ops_rows = [
        ("TikTok app registration (4 platforms)", "Business/Ops", "Start ASAP"),
        ("Cloud environment provisioning", "DevOps/Ops", "VM or managed"),
        ("Domain name & TLS certificates", "Ops", "Required for OAuth"),
        ("TikTok developer portal configuration", "Business/Ops", "Redirect URIs"),
    ]
    for i, (task, owner, notes) in enumerate(ops_rows):
        pdf.table_row([(task, 90), (owner, 40), (notes, 40)], alt=i % 2 == 1)

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        5,
        (
            "This assessment is based on a thorough audit of the Frodo codebase as of "
            f"{date.today().strftime('%B %d, %Y')}. All findings are derived from direct code inspection "
            "of ~205 backend files, 879 tests, Docker configurations, and project documentation."
        ),
    )

    output_path = (
        "/Users/amitkolton/Projects/Tiktok Frodo/Frodo_Technical_Assessment.pdf"
    )
    pdf.output(output_path)
    return output_path


if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF generated: {path}")
