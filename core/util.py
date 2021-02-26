"""Helpers for core modules"""
from datetime import date, datetime, time
from decimal import Context, Decimal, ROUND_HALF_UP


DCM = { # decimal context map
    "number": Context(prec=None, rounding=ROUND_HALF_UP),
    "number_1dp_comma_decimal": Context(prec=1, rounding=ROUND_HALF_UP),
    "number_1dp": Context(prec=1, rounding=ROUND_HALF_UP),
    "number_2dp_comma_decimal": Context(prec=2, rounding=ROUND_HALF_UP),
    "number_2dp": Context(prec=2, rounding=ROUND_HALF_UP),
    "number_3dp_comma_decimal": Context(prec=3, rounding=ROUND_HALF_UP),
    "number_3dp": Context(prec=3, rounding=ROUND_HALF_UP),
    "number_4dp_comma_decimal": Context(prec=4, rounding=ROUND_HALF_UP),
    "number_4dp": Context(prec=4, rounding=ROUND_HALF_UP),
    "number_comma_decimal": Context(prec=None, rounding=ROUND_HALF_UP),
}


record_type_map = {
    "date_dmy": (
        lambda d: date.strptime(d, "%d-%m-%Y"),
        lambda d: d.strftime("%d-%m-%Y"),
        "DATE",
    ),
    "date_mdy": (
        lambda d: date.strptime(d, "%m-%d-%Y"),
        lambda d: d.strftime("%m-%d-%Y"),
        "DATE",
    ),
    "date_ymd": (
        lambda d: date.strptime(d, "%Y-%m-%d"),
        lambda d: d.strftime("%Y-%m-%d"),
        "DATE",
    ),
    "datetime_dmy": (
        lambda d: datetime.strptime(d, "%d-%m-%Y %H:%M"),
        lambda d: d.strftime("%d-%m-%Y %H:%M"),
        "DATETIME",
    ),
    "datetime_mdy": (
        lambda d: datetime.strptime(d, "%m-%d-%Y %H:%M"),
        lambda d: d.strftime("%m-%d-%Y %H:%M"),
        "DATETIME",
    ),
    "datetime_ymd": (
        lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M"),
        lambda d: d.strftime("%Y-%m-%d %H:%M"),
        "DATETIME",
    ),
    "datetime_seconds_dmy": (
        lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M:%S"),
        lambda d: d.strftime("%Y-%m-%d %H:%M:%S"),
        "DATETIME",
    ),
    "datetime_seconds_mdy": (
        lambda d: datetime.strptime(d, "%m-%d-%Y %H:%M:%S"),
        lambda d: d.strftime("%m-%d-%Y %H:%M:%S"),
        "DATETIME",
    ),
    "datetime_seconds_ymd": (
        lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M:%S"),
        lambda d: d.strftime("%Y-%m-%d %H:%M:%S"),
        "DATETIME",
    ),
    "email": (lambda s: s, lambda s: s, "TEXT",),
    "integer": (int, str, "INT",),
    "alpha_only": (lambda s: s, lambda s: s, "TEXT",),
    "number": (
        lambda n: Decimal(sub(r",", ".", n), context=DCM["number"]),
        lambda n: str(n),
        "FLOAT",
    ),
    "number_1dp_comma_decimal": (
        lambda n: Decimal(
            sub(r",", ".", n), context=DCM["number_1dp_comma_decimal"]
        ),
        lambda n: sub(r"\.", ",", str(n)),
        "FLOAT",
    ),
    "number_1dp": (
        lambda n: Decimal(n, context=DCM["number_1dp"]),
        lambda n: str(n),
        "FLOAT",
    ),
    "number_2dp_comma_decimal": (
        lambda n: Decimal(
            sub(r",", ".", n), context=DCM["number_2dp_comma_decimal"]
        ),
        lambda n: sub(r"\.", ",", str(n)),
        "FLOAT",
    ),
    "number_2dp": (
        lambda n: Decimal(n, context=DCM["number_2dp"]),
        lambda n: str(n),
        "FLOAT",
    ),
    "number_3dp_comma_decimal": (
        lambda n: Decimal(
            sub(r",", ".", n), context=DCM["number_3dp_comma_decimal"]
        ),
        lambda n: sub(r"\.", ",", str(n)),
        "FLOAT",
    ),
    "number_3dp": (
        lambda n: Decimal(n, context=DCM["number_3dp"]),
        lambda n: str(n),
        "FLOAT",
    ),
    "number_4dp_comma_decimal": (
        lambda n: Decimal(
            sub(r",", ".", n), context=DCM["number_4dp_comma_decimal"]
        ),
        lambda n: sub(r"\.", ",", str(n)),
        "FLOAT",
    ),
    "number_4dp": (
        lambda n: Decimal(n, context=DCM["number_4dp"]),
        lambda n: str(n),
        "FLOAT",
    ),
    "number_comma_decimal": (
        lambda n: Decimal(
            sub(r",", ".", n), context=DCM["number_comma_decimal"]
        ),
        lambda n: sub(r"\.", ",", str(n)),
        "FLOAT",
    ),
    "phone_australia": (lambda s: s, lambda s: s, "TEXT",),
    "phone": (lambda s: s, lambda s: s, "TEXT",),
    "postalcode_australia": (lambda s: s, lambda s: s, "TEXT",),
    "postalcode_canada": (lambda s: s, lambda s: s, "TEXT",),
    "ssn": (lambda s: s, lambda s: s, "TEXT",),
    "time": (
        lambda t: time.strptime(t, "%H:%M"),
        lambda t: t.strftime("%H:%M"),
        "TIME",
    ),
    "time_mm_ss": (
        lambda t: time.strptime(t, "%M:%S"),
        lambda t: t.strftime("%M:%S"),
        "TIME",
    ),
    "vmrn": (lambda s: s, lambda s: s, "TEXT",),
    "Zipcode": (lambda s: s, lambda s: s, "TEXT",),
    "": (lambda s: s, lambda s: s, "TEXT",),
}
