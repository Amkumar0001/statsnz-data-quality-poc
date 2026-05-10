from __future__ import annotations

import great_expectations as gx
import pandas as pd
from great_expectations import expectations as gxe
from great_expectations.core.expectation_validation_result import (
    ExpectationSuiteValidationResult,
)
from great_expectations.expectations.expectation import Expectation


def cpi_expectations() -> list[Expectation]:
    """Canonical Great Expectations definitions for the CPI dataset.

    Each expectation maps to a data-quality dimension we care about:
    completeness, validity, uniqueness, and value-range sanity.
    Returned as a plain list so callers can introspect without an
    active GX data context.
    """
    return [
        gxe.ExpectColumnToExist(column="Series_reference"),
        gxe.ExpectColumnToExist(column="Period"),
        gxe.ExpectColumnToExist(column="Data_value"),
        gxe.ExpectColumnValuesToNotBeNull(column="Series_reference"),
        gxe.ExpectColumnValuesToNotBeNull(column="Period"),
        gxe.ExpectColumnValuesToNotBeNull(column="Data_value"),
        gxe.ExpectColumnValuesToBeBetween(column="Data_value", min_value=0, max_value=10000),
        gxe.ExpectColumnValuesToMatchRegex(
            column="Series_reference", regex=r"^CPIQ\.[A-Z0-9]+$"
        ),
        gxe.ExpectColumnValuesToMatchRegex(
            column="Period", regex=r"^\d{4}\.(?:03|06|09|12)$"
        ),
        gxe.ExpectColumnValuesToBeInSet(column="STATUS", value_set=["F", "R", "P"]),
        gxe.ExpectCompoundColumnsToBeUnique(column_list=["Series_reference", "Period"]),
        gxe.ExpectTableRowCountToBeBetween(min_value=1, max_value=100000),
    ]


def validate_dataframe(df: pd.DataFrame) -> ExpectationSuiteValidationResult:
    """Validate a DataFrame against the CPI suite using an ephemeral GX context."""
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas("cpi_pandas")
    asset = data_source.add_dataframe_asset(name="cpi_asset")
    batch_definition = asset.add_batch_definition_whole_dataframe("whole_df")

    suite = context.suites.add(gx.ExpectationSuite(name="cpi_quarterly"))
    for expectation in cpi_expectations():
        suite.add_expectation(expectation)

    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(name="cpi_validation", data=batch_definition, suite=suite)
    )
    return validation_definition.run(batch_parameters={"dataframe": df})
