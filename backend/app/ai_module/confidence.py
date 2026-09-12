from .schemas import (
    InvoiceFields,
    AIWarning,
)


CRITICAL_FIELDS = [

    "supplier_name",

    "invoice_number",

    "invoice_date",

    "total_amount",

]


CONFIDENCE_THRESHOLD = 0.75


def calculate_overall_confidence(
    fields: InvoiceFields
) -> float:

    supplier_score = (
        fields
        .supplier_name
        .confidence
    )

    invoice_number_score = (
        fields
        .invoice_number
        .confidence
    )

    invoice_date_score = (
        fields
        .invoice_date
        .confidence
    )

    total_score = (
        fields
        .total_amount
        .confidence
    )


    score = (

        supplier_score * 0.25

        + invoice_number_score * 0.25

        + invoice_date_score * 0.20

        + total_score * 0.30

    )


    return round(
        min(
            max(score, 0.0),
            1.0
        ),
        3
    )


def get_confidence_level(
    confidence: float
) -> str:

    if confidence >= 0.90:

        return "HIGH"

    elif confidence >= 0.75:

        return "MEDIUM"

    else:

        return "LOW"


def build_review_warnings(
    fields: InvoiceFields
) -> list[AIWarning]:

    warnings = []


    for field_name in CRITICAL_FIELDS:

        field = getattr(
            fields,
            field_name
        )


        if field.value is None:

            warnings.append(

                AIWarning(

                    code=f"MISSING_{field_name.upper()}",

                    message=(
                        f"{field_name} could not "
                        f"be extracted."
                    ),

                    severity="HIGH",

                    field=field_name,

                )

            )

            continue


        if (
            field.confidence
            < CONFIDENCE_THRESHOLD
        ):

            warnings.append(

                AIWarning(

                    code=(
                        f"LOW_"
                        f"{field_name.upper()}_"
                        f"CONFIDENCE"
                    ),

                    message=(
                        f"{field_name} confidence "
                        f"is only "
                        f"{field.confidence:.2f}."
                    ),

                    severity="HIGH",

                    field=field_name,

                )

            )


    optional_fields = [

        "due_date",

        "purchase_order_number",

        "currency",

        "subtotal",

        "tax_amount",

    ]


    for field_name in optional_fields:

        field = getattr(
            fields,
            field_name
        )


        if (
            field.value is not None
            and field.confidence
            < CONFIDENCE_THRESHOLD
        ):

            warnings.append(

                AIWarning(

                    code=(
                        f"LOW_"
                        f"{field_name.upper()}_"
                        f"CONFIDENCE"
                    ),

                    message=(
                        f"{field_name} was extracted "
                        f"with low confidence."
                    ),

                    severity="MEDIUM",

                    field=field_name,

                )

            )


    return warnings


def requires_review(
    warnings: list[AIWarning]
) -> bool:

    for warning in warnings:

        if warning.severity == "HIGH":

            return True


    return False