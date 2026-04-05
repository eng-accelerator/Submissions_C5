import base64
from io import BytesIO
from PIL import Image
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from schemas.outputs import PhishingReport


def resize_image(image_bytes: bytes, max_size=(800, 800)) -> bytes:
    """
    Resizes an image given as bytes so that its dimensions do not exceed max_size,
    maintaining aspect ratio, to save tokens.
    """
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            output_buffer = BytesIO()
            img.save(output_buffer, format="JPEG")
            return output_buffer.getvalue()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_bytes


def analyze_suspicious_email_image(image_bytes: bytes) -> dict:
    """
    Takes raw image bytes, resizes them, converts to base64, and sends it to the LLM
    for phishing analysis matching standard Pydantic payload models.
    """
    parser = PydanticOutputParser(pydantic_object=PhishingReport)

    SYSTEM_PROMPT = f"""You are an elite Cyber Threat Intelligence Analyst specializing in advanced email security.
The user will provide a screenshot of an email. Your job is to deeply analyze this email for the following threat vectors:
1. Spear Phishing (highly targeted contextual attacks).
2. HTML Smuggling (obfuscated JavaScript/HTML payloads).
3. Thread Hijacking (replying to compromised existing legitimate email threads).
4. Business Email Compromise / BEC (financial fraud, executive impersonation).
5. Malicious Attachments (suspicious file extensions, macros).
6. Credential Harvesting (fake login portals).
7. Spoofing (domain typosquatting, mismatched sender addresses).
8. Clone Phishing (copying legitimate emails and replacing safe links with malicious ones).
9. Zero-day Exploits (unusual browser behaviors instructed in the email body).
10. Whaling (targeting C-level executives or high-value individuals).
11. Quishing (QR code phishing leading to malicious domains).
12. Malware Links in Email Clients (obfuscated or risky hyperlinked URLs).

Return your analysis strictly conforming to the JSON schema.
{{format_instructions}}
"""

    optimized_img_bytes = resize_image(image_bytes)
    base64_image = base64.b64encode(optimized_img_bytes).decode("utf-8")

    or_key = os.environ.get("OPENROUTER_API_KEY", "")
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if or_key:
        raw_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            temperature=0,
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key,
        )
    elif api_key.startswith("sk-or"):
        raw_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            temperature=0,
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    else:
        raw_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT.format(
                format_instructions=parser.get_format_instructions()
            )
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Please analyze this suspicious email screenshot and provide output strictly in the requested JSON structure.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]
        ),
    ]

    try:
        response = raw_llm.invoke(messages)
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        report = parser.parse(content)
        return {"report_data": report.model_dump()}
    except Exception as e:
        print(f"Error during email image analysis: {e}")
        return {"report_data": {"error": f"Failed parsing: {str(e)}"}}
