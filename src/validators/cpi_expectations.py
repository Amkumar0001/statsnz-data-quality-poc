from __future__ import annotations

import great_expectations as gx
import pandas as pd
from great_expectations import expectations as gxe
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.core.expectation_validation_result import (
    ExpectationSuiteValidationResult,
)


def build_cpi_suite() -> ExpectationSuite:
    """Define the canonical Great Expectations suite for the CPI dataset."""
    suite = ExpectationSuite(name="cpi_quarterly")
    suite.add_expectation(gxe.ExpectColumnToExist(column="Series_reference"))
    suite.add_expectation(gxe.ExpectColumnToExist(column="Period"))
    suite.add_expectation(gxe.ExpectColumnToExist(column="Data_value"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="Series_reference"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="Period"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="Data_value"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="Data_value", min_value=0, max_value=10000)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(
            column="Series_reference", regex=r"^CPIQ\.[A-Z0-9]+$"
        )
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(
            column="Period", regex=r"^\d{4}\.(?:03|06|09|12)$"
        )
    )
    suite.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="STATUS", value_set=["F", "R", "P"]))
    suite.add_expectation(
        gxe.ExpectCompoundColumnsToBeUnique(column_list=["Series_reference", "Period"])
    )
    suite.add_expectation(gxe.ExpectTableRowCountToBeBetween(min_value=1, max_value=100000))
    return suite


def validate_dataframe(df: pd.DataFrame) -> ExpectationSuiteValidationResult:
    """Validate a DataFrame against the CPI suite using an ephemeral GX context."""
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas("cpi_pandas")
    asset = data_source.add_dataframe_asset(name="cpi_asset")
    batch_definition = asset.add_batch_definition_whole_dataframe("whole_df")

    suite = context.suites.add(build_cpi_suite())
    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(name="cpi_validation", data=batch_definition, suite=suite)
    )
    return validation_definition.run(batch_parameters={"dataframe": df})
