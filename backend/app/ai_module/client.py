import base64
import os

import anthropic
from dotenv import load_dotenv

from .exceptions import ModelCallError
from .prompts import SYSTEM_PROMPT, VISION_PROMPT, build_text_prompt

load_dotenv()

MAX_TOKENS = 4096


def _build_image_block(image_data_url: str) -> dict:
    """Convert a data: URL or plain http(s) URL into an Anthropic content block."""

    if image_data_url.startswith("data:"):
        header, _, data = image_data_url.partition(",")
        media_type = header[len("data:"):].split(";")[0] or "image/png"

        block_type = "document" if media_type == "application/pdf" else "image"

        return {
            "type": block_type,
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": data,
            },
        }

    return {
        "type": "image",
        "source": {
            "type": "url",
            "url": image_data_url,
        },
    }


class InvoiceLLMClient:
    """Thin wrapper around the Claude API for invoice extraction."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("MODEL_API_KEY")
        model_name = os.getenv("MODEL_NAME", "claude-opus-5")
        base_url = os.getenv("MODEL_BASE_URL")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY (or MODEL_API_KEY) is missing.")

        client_arguments = {"api_key": api_key}
        if base_url:
            client_arguments["base_url"] = base_url

        self.client = anthropic.Anthropic(**client_arguments)
        self.model = model_name

    def _create(self, user_content) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                output_config={"effort": "low"},
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_content}],
            )
        except anthropic.AuthenticationError as error:
            raise ModelCallError("Invalid Claude API key.") from error
        except anthropic.RateLimitError as error:
            raise ModelCallError("Rate limited by Claude API.") from error
        except anthropic.APIStatusError as error:
            raise ModelCallError(f"Claude API error ({error.status_code}): {error.message}") from error
        except anthropic.APIConnectionError as error:
            raise ModelCallError(f"Network error contacting Claude API: {error}") from error

        content = next((block.text for block in response.content if block.type == "text"), None)

        if not content:
            raise ModelCallError("Model returned empty response.")

        return content

    def extract_text_invoice(self, invoice_text: str) -> str:
        return self._create(build_text_prompt(invoice_text))

    def extract_image_invoice(self, image_data_urls: list[str]) -> str:
        if not image_data_urls:
            raise ValueError("No invoice images provided.")

        user_content = [{"type": "text", "text": VISION_PROMPT}]
        user_content.extend(_build_image_block(url) for url in image_data_urls)

        return self._create(user_content)

    def repair_json(self, broken_response: str) -> str:
        repair_prompt = f"""
The following invoice extraction response is malformed JSON.

Correct it so that it exactly follows the required invoice extraction
JSON structure.

Return JSON ONLY.

BROKEN RESPONSE:

{broken_response}
"""
        return self._create(repair_prompt)
