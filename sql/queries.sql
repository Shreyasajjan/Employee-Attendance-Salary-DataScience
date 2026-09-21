-- Core employee/payroll queries

SELECT * FROM employees LIMIT 10;

SELECT Employee_ID, Employee_Name, Attendance_Percentage
FROM payroll
ORDER BY Attendance_Percentage DESC;

SELECT Employee_ID, Employee_Name, Attendance_Percentage
FROM payroll
WHERE Attendance_Percentage < 80
ORDER BY Attendance_Percentage;

SELECT Department, ROUND(AVG(Monthly_Salary), 2) AS avg_salary
FROM payroll
GROUP BY Department
ORDER BY avg_salary DESC;

SELECT Department, ROUND(AVG(Attendance_Percentage), 2) AS avg_attendance
FROM payroll
GROUP BY Department
ORDER BY avg_attendance DESC;

SELECT Employee_ID, Employee_Name, Overtime_Hours, Overtime_Pay
FROM payroll
ORDER BY Overtime_Hours DESC
LIMIT 10;

SELECT Employee_ID, Employee_Name, Net_Salary
FROM payroll
ORDER BY Net_Salary DESC
LIMIT 10;

SELECT Employee_ID, Employee_Name, PF_Deduction, Tax_Deduction, Other_Deductions
FROM payroll
WHERE PF_Deduction + Tax_Deduction + Other_Deductions > 0;

SELECT ROUND(SUM(Net_Salary), 2) AS total_salary_expense
FROM payroll;

SELECT Department, ROUND(AVG(Overtime_Hours), 2) AS avg_overtime
FROM payroll
GROUP BY Department
ORDER BY avg_overtime DESC;

SELECT Employee_ID, Employee_Name, Gross_Salary, Net_Salary,
       Overtime_Pay, Attendance_Bonus
FROM payroll
ORDER BY Employee_Name;
