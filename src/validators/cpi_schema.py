from __future__ import annotations

import pandera.pandas as pa

CPI_STATUSES = ["F", "R", "P"]

cpi_schema = pa.DataFrameSchema(
    columns={
        "Series_reference": pa.Column(
            "string",
            checks=pa.Check.str_matches(r"^CPIQ\.[A-Z0-9]+$"),
            nullable=False,
        ),
        "Period": pa.Column(
            "string",
            checks=pa.Check.str_matches(r"^\d{4}\.(?:03|06|09|12)$"),
            nullable=False,
        ),
        "Data_value": pa.Column(
            float,
            checks=[pa.Check.greater_than(0), pa.Check.less_than(10000)],
            nullable=False,
        ),
        "STATUS": pa.Column(
            "string",
            checks=pa.Check.isin(CPI_STATUSES),
            nullable=False,
        ),
        "UNITS": pa.Column("string", nullable=False),
        "Subject": pa.Column("string", nullable=False),
        "Group": pa.Column("string", nullable=False),
        "Series_title_1": pa.Column("string", nullable=False),
    },
    strict=True,
    coerce=False,
    unique=["Series_reference", "Period"],
)
