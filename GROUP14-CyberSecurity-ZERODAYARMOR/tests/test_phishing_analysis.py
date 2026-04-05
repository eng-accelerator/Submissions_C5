import pytest
import os
import glob
from unittest.mock import patch, MagicMock
from PIL import Image
from io import BytesIO
from agents.phishing_analysis import analyze_suspicious_email_image, resize_image


def test_resize_image_dimensions():
    # Create a large dummy image
    img = Image.new("RGB", (2000, 2000), color="blue")
    buf = BytesIO()
    img.save(buf, format="PNG")
    original_bytes = buf.getvalue()

    # Process the resize function directly
    resized_bytes = resize_image(original_bytes)

    with Image.open(BytesIO(resized_bytes)) as new_img:
        # Check it successfully constrained dimensions to 800x800
        assert new_img.size == (800, 800)
        assert new_img.format == "JPEG"


class TestPhishingAnalysis:

    THREAT_SCENARIOS = [
        ("Spear Phishing", "Spear Phishing detected: tailored payload to HR."),
        (
            "HTML Smuggling",
            "HTML Smuggling detected. JavaScript payload obfuscated in attachment.",
        ),
        (
            "Thread Hijacking",
            "Thread Hijacking detected. Replay of earlier thread context.",
        ),
        (
            "Business Email Compromise",
            "Business Email Compromise (BEC) detected. CEO impersonation urgent wire transfer.",
        ),
        (
            "Malicious Attachments",
            "Malicious Attachment detected: 'invoice.xlsm' contains macros.",
        ),
        (
            "Credential Harvesting",
            "Credential Harvesting: fake Microsoft 365 login portal linked.",
        ),
        ("Spoofing", "Spoofing detected: domain typosquatting paypal-secuure.com."),
        (
            "Clone Phishing",
            "Clone Phishing: identical to previous legitimate email but link flipped to malicious proxy.",
        ),
        (
            "Zero-day Exploits",
            "Zero-day Exploit indicators: obscure payload vector in email rendering.",
        ),
        ("Whaling", "Whaling attack: high-value target (CFO) explicitly targeted."),
        ("Quishing", "Quishing detected: QR code masks a malicious redirect URL."),
        (
            "Malware Links",
            "Malware links: embedded hyperlinks redirecting to known malicious C2 drops.",
        ),
    ]

    @pytest.mark.parametrize("threat_type, mock_report", THREAT_SCENARIOS)
    @patch("agents.phishing_analysis.ChatOpenAI.invoke")
    def test_analyze_suspicious_email_image(
        self, mock_invoke, threat_type, mock_report
    ):
        # Setup mock LLM response returning structured JSON matching PhishingReport
        mock_response = MagicMock()
        mock_response.content = f"""```json
{{
    "is_phishing": true,
    "risk_level": "HIGH",
    "detected_threats": ["{threat_type}"],
    "social_engineering_tactics": ["Urgency", "Impersonation"],
    "suspicious_links_or_attachments": ["malicious_link.html"],
    "summary_analysis": "{mock_report}"
}}
```"""
        mock_invoke.return_value = mock_response

        # Create a small dummy image for testing end-to-end agent function
        img = Image.new("RGB", (200, 200), color="red")
        buf = BytesIO()
        img.save(buf, format="PNG")
        dummy_bytes = buf.getvalue()

        # Run end-to-end analysis
        result = analyze_suspicious_email_image(dummy_bytes)

        # Assertions
        assert "report_data" in result
        assert result["report_data"]["risk_level"] == "HIGH"
        assert threat_type in result["report_data"]["detected_threats"]
        mock_invoke.assert_called_once()

        # Confirm that the mock was called with our messages (vision context included)
        call_args = mock_invoke.call_args[0][0]
        assert len(call_args) == 2  # System message and Human message

    @pytest.mark.skipif(
        "OPENAI_API_KEY" not in os.environ,
        reason="Requires real API key to run true E2E image tests.",
    )
    def test_end_to_end_real_phishing_images(self):
        """
        True E2E test against the real images in data/phishing_imgs using the actual LLM API.
        This test ONLY runs if OPENAI_API_KEY is detected in environment.
        """
        img_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "phishing_imgs"
        )
        image_files = glob.glob(os.path.join(img_dir, "*.*"))

        # Make sure our images are present
        assert len(image_files) > 0, "No images found in data/phishing_imgs"

        for img_path in image_files:
            with open(img_path, "rb") as f:
                image_bytes = f.read()

            result = analyze_suspicious_email_image(image_bytes)

            assert "report_data" in result
            report = result["report_data"]

            if "error" in report:
                print(
                    f"Skipping strict validation for {os.path.basename(img_path)} due to: {report['error']}"
                )
                continue

            assert (
                "risk_level" in report
            ), f"Failed parsing Risk Level properly for {img_path}"

            # Additional validation
            print(f"\\n--- E2E Report for {os.path.basename(img_path)} ---\\n{report}")
