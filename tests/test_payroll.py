import pytest
from src.payroll import (
    calculate_attendance_percentage,
    calculate_overtime_pay,
    calculate_attendance_bonus,
)

def test_attendance_percentage():
    assert calculate_attendance_percentage(26, 26) == 100
    assert calculate_attendance_percentage(0, 26) == 0

def test_overtime_zero():
    assert calculate_overtime_pay(52000, 0, 26) == 0

def test_overtime_positive():
    value = calculate_overtime_pay(52000, 2, 26)
    assert value > 0

def test_bonus_eligible():
    assert calculate_attendance_bonus(50000, 96, 5) == 2500

def test_bonus_not_eligible():
    assert calculate_attendance_bonus(50000, 90, 5) == 0
    assert calculate_attendance_bonus(50000, 96, 0) == 0
