import resend
import logging
from app.providers.base_email import EmailService
from app.schemas.analysis import AnalysisResult
from app.config import settings

logger = logging.getLogger(__name__)


def build_report_html(user_email: str, analysis: AnalysisResult) -> str:
    """Build a clean, mobile-friendly HTML email for the analysis report."""

    concerns_html = ""
    if analysis.top_concerns:
        pills = "".join(
            f'<span style="display:inline-block;background:#fde8e0;color:#c0533a;'
            f'padding:4px 14px;border-radius:20px;font-size:13px;margin:3px 4px 3px 0;">{c}</span>'
            for c in analysis.top_concerns
        )
        concerns_html = f'<tr><td style="padding:16px 24px;"><h3 style="margin:0 0 10px;color:#1a1a1a;font-size:16px;">Top Concerns</h3>{pills}</td></tr>'

    routine_html = ""
    if analysis.routine:
        morning = "".join(f"<li style='margin-bottom:6px;'>{s}</li>" for s in (analysis.routine.morning or []))
        evening = "".join(f"<li style='margin-bottom:6px;'>{s}</li>" for s in (analysis.routine.evening or []))
        routine_html = f"""
        <tr><td style="padding:16px 24px;">
            <h3 style="margin:0 0 10px;color:#1a1a1a;font-size:16px;">Suggested Routine</h3>
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
                <td style="vertical-align:top;width:50%;padding-right:8px;">
                    <p style="font-weight:bold;font-size:12px;color:#888;text-transform:uppercase;margin:0 0 6px;">☀️ Morning</p>
                    <ul style="padding-left:18px;margin:0;font-size:14px;color:#333;">{morning}</ul>
                </td>
                <td style="vertical-align:top;width:50%;padding-left:8px;">
                    <p style="font-weight:bold;font-size:12px;color:#888;text-transform:uppercase;margin:0 0 6px;">🌙 Evening</p>
                    <ul style="padding-left:18px;margin:0;font-size:14px;color:#333;">{evening}</ul>
                </td>
            </tr></table>
        </td></tr>"""

    nudges_html = ""
    if analysis.lifestyle_nudges:
        items = "".join(f"<li style='margin-bottom:6px;'>{n}</li>" for n in analysis.lifestyle_nudges)
        nudges_html = f"""
        <tr><td style="padding:16px 24px;">
            <h3 style="margin:0 0 10px;color:#1a1a1a;font-size:16px;">Lifestyle Tips</h3>
            <ul style="padding-left:18px;margin:0;font-size:14px;color:#333;">{items}</ul>
        </td></tr>"""

    note_html = ""
    if analysis.encouragement_note:
        note_html = f"""
        <tr><td style="padding:16px 24px;">
            <div style="background:#fef9e7;border:1px solid #fde68a;border-radius:12px;padding:16px;text-align:center;">
                <p style="margin:0;font-style:italic;color:#92700c;font-size:14px;">"{analysis.encouragement_note}"</p>
            </div>
        </td></tr>"""

    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="margin:0;padding:0;background:#f5ebe0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;margin-top:24px;margin-bottom:24px;">
            <!-- Header -->
            <tr><td style="background:linear-gradient(135deg,#1a1a1a,#333);padding:32px 24px;text-align:center;">
                <h1 style="margin:0;color:#fff;font-size:28px;font-weight:300;">Skin<em style="color:#c0533a;">Scan</em></h1>
                <p style="margin:8px 0 0;color:rgba(255,255,255,0.7);font-size:14px;">Your Cosmetic Analysis Report</p>
            </td></tr>

            <!-- Summary -->
            <tr><td style="padding:24px;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#faf6f1;border-radius:12px;overflow:hidden;">
                    <tr>
                        <td style="padding:16px;text-align:center;width:50%;border-right:1px solid #e8ddd4;">
                            <p style="margin:0;font-size:12px;color:#888;text-transform:uppercase;">Skin Type</p>
                            <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#1a1a1a;">{analysis.skin_type or '—'}</p>
                        </td>
                        <td style="padding:16px;text-align:center;width:50%;">
                            <p style="margin:0;font-size:12px;color:#888;text-transform:uppercase;">Skin Tone</p>
                            <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#1a1a1a;">{analysis.skin_tone or '—'}</p>
                        </td>
                    </tr>
                </table>
            </td></tr>

            {concerns_html}
            {routine_html}
            {nudges_html}
            {note_html}

            <!-- Footer -->
            <tr><td style="padding:24px;text-align:center;border-top:1px solid #f0e8df;">
                <p style="margin:0 0 8px;font-size:12px;color:#999;">Cosmetic analysis only · Not medical advice</p>
                <p style="margin:0;font-size:11px;color:#bbb;">This email was sent to {user_email}. You can delete your data at any time.</p>
            </td></tr>
        </table>
    </body></html>
    """


class ResendEmailService(EmailService):
    def __init__(self):
        resend.api_key = settings.resend_api_key

    async def send_report(self, user, analysis: AnalysisResult) -> bool:
        if not settings.email_configured:
            logger.info("Email not configured — skipping report send")
            return True

        try:
            html_content = build_report_html(user.email, analysis)

            params: resend.Emails.SendParams = {
                "from": f"{settings.resend_from_name} <{settings.resend_from_email}>",
                "to": [user.email],
                "subject": "Your SkinScan Analysis Report ✨",
                "html": html_content,
            }

            resend.Emails.send(params)
            logger.info(f"Report email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {e}")
            return False
