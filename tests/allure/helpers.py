"""
Allure step helper functions for starward test suite.

These helpers wrap common test patterns with Allure steps and attachments
for better visibility in test reports.

Example:
    from tests.allure.helpers import step_compute, step_verify_range

    def test_altitude_calculation(self, observer):
        alt = step_compute("altitude", target_altitude, target, observer, jd)
        step_verify_range("altitude", alt.degrees, -90, 90)
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional, Type, Union

import allure
import pytest


def attach_value(name: str, value: Any, as_type: str = "text") -> None:
    """
    Attach a value to the current Allure step for visibility.

    Args:
        name: Display name for the attachment
        value: Value to attach (will be converted to string)
        as_type: Attachment type ("text", "json", "csv")
    """
    type_map = {
        "text": allure.attachment_type.TEXT,
        "json": allure.attachment_type.JSON,
        "csv": allure.attachment_type.CSV,
    }
    allure.attach(
        str(value),
        name=name,
        attachment_type=type_map.get(as_type, allure.attachment_type.TEXT)
    )


def step_compute(
    name: str,
    func: Callable,
    *args,
    attach_result: bool = True,
    **kwargs
) -> Any:
    """
    Execute a computation within an Allure step.

    Args:
        name: Description of what is being computed
        func: Function to call
        *args: Positional arguments for func
        attach_result: Whether to attach the result value
        **kwargs: Keyword arguments for func

    Returns:
        The result of func(*args, **kwargs)

    Example:
        alt = step_compute("target altitude", target_altitude, target, observer, jd)
    """
    with allure.step(f"Compute {name}"):
        result = func(*args, **kwargs)
        if attach_result and result is not None:
            attach_value(name, result)
        return result


def step_parse(
    name: str,
    func: Callable,
    input_value: str,
    attach_input: bool = True,
    attach_result: bool = True,
) -> Any:
    """
    Parse a string value within an Allure step.

    Args:
        name: Description of what is being parsed
        func: Parsing function to call
        input_value: String to parse
        attach_input: Whether to attach the input string
        attach_result: Whether to attach the parsed result

    Returns:
        The parsed result

    Example:
        coords = step_parse("coordinates", ICRSCoord.parse, "12h 30m +45°")
    """
    with allure.step(f"Parse {name}"):
        if attach_input:
            attach_value("input", input_value)
        result = func(input_value)
        if attach_result and result is not None:
            attach_value("parsed", result)
        return result


def step_verify_range(
    name: str,
    value: float,
    min_val: float,
    max_val: float,
    include_bounds: bool = True,
) -> None:
    """
    Verify a value falls within an expected range.

    Args:
        name: Description of the value being checked
        value: Actual value to verify
        min_val: Minimum expected value
        max_val: Maximum expected value
        include_bounds: If True, use <= and >=; if False, use < and >

    Raises:
        AssertionError: If value is outside the range

    Example:
        step_verify_range("altitude", alt.degrees, -90, 90)
    """
    with allure.step(f"Verify {name} in [{min_val}, {max_val}]"):
        attach_value(name, value)
        if include_bounds:
            assert min_val <= value <= max_val, (
                f"{name}={value} outside range [{min_val}, {max_val}]"
            )
        else:
            assert min_val < value < max_val, (
                f"{name}={value} outside range ({min_val}, {max_val})"
            )


def step_verify_approx(
    name: str,
    actual: float,
    expected: float,
    rel_tol: float = 0.01,
    abs_tol: Optional[float] = None,
) -> None:
    """
    Verify approximate equality of two values.

    Args:
        name: Description of the value being checked
        actual: Actual value
        expected: Expected value
        rel_tol: Relative tolerance (default 1%)
        abs_tol: Absolute tolerance (optional)

    Raises:
        AssertionError: If values are not approximately equal

    Example:
        step_verify_approx("airmass", X, 1.0, rel_tol=0.05)
    """
    with allure.step(f"Verify {name} ≈ {expected}"):
        attach_value("actual", actual)
        attach_value("expected", expected)
        if abs_tol is not None:
            assert actual == pytest.approx(expected, rel=rel_tol, abs=abs_tol)
        else:
            assert actual == pytest.approx(expected, rel=rel_tol)


def step_verify_isinstance(
    name: str,
    value: Any,
    expected_type: Union[Type, tuple],
) -> None:
    """
    Verify a value is an instance of expected type(s).

    Args:
        name: Description of the value being checked
        value: Value to check
        expected_type: Expected type or tuple of types

    Raises:
        AssertionError: If value is not an instance of expected_type

    Example:
        step_verify_isinstance("altitude", alt, Angle)
    """
    type_name = (
        expected_type.__name__ if isinstance(expected_type, type)
        else str(expected_type)
    )
    with allure.step(f"Verify {name} is {type_name}"):
        attach_value(name, value)
        attach_value("type", type(value).__name__)
        assert isinstance(value, expected_type), (
            f"{name} is {type(value).__name__}, expected {type_name}"
        )


def step_verify_order(
    name: str,
    values: list,
    labels: Optional[list] = None,
    descending: bool = False,
) -> None:
    """
    Verify a list of values is in order.

    Args:
        name: Description of the ordering being checked
        values: List of comparable values
        labels: Optional labels for each value
        descending: If True, check descending order

    Raises:
        AssertionError: If values are not in expected order

    Example:
        step_verify_order("event times", [rise.jd, transit.jd, set_time.jd],
                         labels=["rise", "transit", "set"])
    """
    with allure.step(f"Verify {name} ordering"):
        if labels:
            for i, (label, val) in enumerate(zip(labels, values)):
                attach_value(f"{i+1}. {label}", val)
        else:
            for i, val in enumerate(values):
                attach_value(f"value[{i}]", val)

        for i in range(len(values) - 1):
            if descending:
                assert values[i] >= values[i + 1], (
                    f"Order violation at index {i}: {values[i]} < {values[i+1]}"
                )
            else:
                assert values[i] <= values[i + 1], (
                    f"Order violation at index {i}: {values[i]} > {values[i+1]}"
                )


def step_verify_relationship(
    description: str,
    val1: Any,
    operator: str,
    val2: Any,
    label1: str = "left",
    label2: str = "right",
) -> None:
    """
    Verify a relationship between two values.

    Args:
        description: Description of what relationship is being verified
        val1: Left-hand value
        operator: Comparison operator ("<", "<=", ">", ">=", "==", "!=")
        val2: Right-hand value
        label1: Label for val1
        label2: Label for val2

    Raises:
        AssertionError: If relationship does not hold

    Example:
        step_verify_relationship("transit altitude higher",
                                alt_transit.degrees, ">", alt_now.degrees,
                                "at transit", "now")
    """
    ops = {
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }
    with allure.step(f"Verify {description}"):
        attach_value(label1, val1)
        attach_value(label2, val2)
        attach_value("comparison", f"{val1} {operator} {val2}")
        assert ops[operator](val1, val2), (
            f"Relationship failed: {label1}={val1} {operator} {label2}={val2}"
        )
