import json
import re
from datetime import datetime

from .client import InvoiceLLMClient

from .schemas import (
    InvoiceFields,
    InvoiceAIResult,
)

from .confidence import (
    calculate_overall_confidence,
    get_confidence_level,
    build_review_warnings,
    requires_review,
)

from .exceptions import (
    ModelResponseError,
)


def extract_json(
    raw_response: str
) -> dict:

    if not raw_response:

        raise ModelResponseError(
            "Empty model response."
        )


    text = raw_response.strip()


    # Remove Markdown JSON fences

    text = re.sub(
        r"^```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```",
        "",
        text
    )

    text = re.sub(
        r"```$",
        "",
        text
    )


    # Find first JSON object

    start = text.find("{")

    end = text.rfind("}")


    if (
        start == -1
        or end == -1
    ):

        raise ModelResponseError(
            "No JSON object found."
        )


    json_text = text[
        start:end + 1
    ]


    try:

        return json.loads(
            json_text
        )


    except json.JSONDecodeError as error:

        raise ModelResponseError(
            f"Invalid JSON: {error}"
        ) from error


def normalize_amount(
    value
):

    if value is None:

        return None


    if isinstance(
        value,
        (int, float)
    ):

        return float(value)


    text = str(value)


    text = text.replace(
        ",",
        ""
    )


    text = re.sub(

        r"(?i)"
        r"(LKR|Rs\.?|USD|EUR|GBP)",

        "",

        text

    )


    text = re.sub(

        r"[^\d.\-]",

        "",

        text

    )


    if not text:

        return None


    try:

        return float(text)

    except ValueError:

        return None


def normalize_date(
    value
):

    if not value:

        return None


    value = str(value).strip()


    formats = [

        "%Y-%m-%d",

        "%d/%m/%Y",

        "%d-%m-%Y",

        "%d.%m.%Y",

        "%d %b %Y",

        "%d %B %Y",

        "%b %d, %Y",

        "%B %d, %Y",

    ]


    for date_format in formats:

        try:

            parsed = datetime.strptime(
                value,
                date_format
            )

            return (
                parsed
                .date()
                .isoformat()
            )

        except ValueError:

            continue


    return value


def prepare_field(
    raw_data: dict,
    field_name: str,
    amount: bool = False,
    date: bool = False,
):

    field_data = raw_data.get(
        field_name,
        {}
    )


    if not isinstance(
        field_data,
        dict
    ):

        field_data = {

            "value": field_data,

            "confidence": 0.5,

            "evidence": None,

        }


    value = field_data.get(
        "value"
    )


    confidence = field_data.get(
        "confidence",
        0.0
    )


    evidence = field_data.get(
        "evidence"
    )


    try:

        confidence = float(
            confidence
        )

    except (
        ValueError,
        TypeError
    ):

        confidence = 0.0


    # Some models may return 95
    # instead of 0.95

    if (
        confidence > 1
        and confidence <= 100
    ):

        confidence /= 100


    confidence = max(
        0.0,
        min(
            confidence,
            1.0
        )
    )


    if amount:

        value = normalize_amount(
            value
        )


    if date:

        value = normalize_date(
            value
        )


    return {

        "value": value,

        "confidence": confidence,

        "evidence": evidence,

    }


def build_invoice_fields(
    data: dict
) -> InvoiceFields:

    cleaned = {

        "supplier_name":
            prepare_field(
                data,
                "supplier_name"
            ),

        "invoice_number":
            prepare_field(
                data,
                "invoice_number"
            ),

        "invoice_date":
            prepare_field(
                data,
                "invoice_date",
                date=True
            ),

        "due_date":
            prepare_field(
                data,
                "due_date",
                date=True
            ),

        "purchase_order_number":
            prepare_field(
                data,
                "purchase_order_number"
            ),

        "currency":
            prepare_field(
                data,
                "currency"
            ),

        "subtotal":
            prepare_field(
                data,
                "subtotal",
                amount=True
            ),

        "tax_amount":
            prepare_field(
                data,
                "tax_amount",
                amount=True
            ),

        "discount_amount":
            prepare_field(
                data,
                "discount_amount",
                amount=True
            ),

        "total_amount":
            prepare_field(
                data,
                "total_amount",
                amount=True
            ),

    }


    return InvoiceFields.model_validate(
        cleaned
    )


def process_ai_response(
    raw_response: str,
    client: InvoiceLLMClient,
) -> InvoiceFields:

    try:

        data = extract_json(
            raw_response
        )

        return build_invoice_fields(
            data
        )


    except ModelResponseError:

        # One repair attempt only

        repaired_response = (
            client.repair_json(
                raw_response
            )
        )


        data = extract_json(
            repaired_response
        )


        return build_invoice_fields(
            data
        )


def create_final_result(
    fields: InvoiceFields
) -> InvoiceAIResult:

    overall_confidence = (
        calculate_overall_confidence(
            fields
        )
    )


    confidence_level = (
        get_confidence_level(
            overall_confidence
        )
    )


    warnings = (
        build_review_warnings(
            fields
        )
    )


    needs_review = (
        requires_review(
            warnings
        )
    )


    return InvoiceAIResult(

        success=True,

        fields=fields,

        overall_confidence=(
            overall_confidence
        ),

        confidence_level=(
            confidence_level
        ),

        requires_review=(
            needs_review
        ),

        warnings=warnings,

        error=None,

    )


def extract_invoice_from_text(
    invoice_text: str,
    client: InvoiceLLMClient = None,
) -> InvoiceAIResult:

    if not invoice_text:

        return InvoiceAIResult(

            success=False,

            requires_review=True,

            error=(
                "Invoice text is empty."
            )

        )


    try:

        if client is None:

            client = InvoiceLLMClient()


        raw_response = (
            client.extract_text_invoice(
                invoice_text
            )
        )


        fields = process_ai_response(
            raw_response,
            client
        )


        return create_final_result(
            fields
        )


    except Exception as error:

        return InvoiceAIResult(

            success=False,

            requires_review=True,

            error=str(error),

        )


def extract_invoice_from_images(
    image_data_urls: list[str],
    client: InvoiceLLMClient = None,
) -> InvoiceAIResult:

    if not image_data_urls:

        return InvoiceAIResult(

            success=False,

            requires_review=True,

            error=(
                "No invoice images "
                "were provided."
            )

        )


    try:

        if client is None:

            client = InvoiceLLMClient()


        raw_response = (
            client.extract_image_invoice(
                image_data_urls
            )
        )


        fields = process_ai_response(
            raw_response,
            client
        )


        return create_final_result(
            fields
        )


    except Exception as error:

        return InvoiceAIResult(

            success=False,

            requires_review=True,

            error=str(error),

        )