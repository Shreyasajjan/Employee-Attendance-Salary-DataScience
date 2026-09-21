-- Analytical SQL queries

SELECT Department,
       COUNT(*) AS employees,
       ROUND(AVG(Attendance_Percentage), 2) AS avg_attendance,
       ROUND(AVG(Net_Salary), 2) AS avg_net_salary,
       ROUND(SUM(Net_Salary), 2) AS salary_expense
FROM payroll
GROUP BY Department
ORDER BY salary_expense DESC;

SELECT Department,
       ROUND(SUM(Overtime_Pay), 2) AS overtime_cost,
       ROUND(AVG(Overtime_Hours), 2) AS avg_overtime_hours
FROM payroll
GROUP BY Department
ORDER BY overtime_cost DESC;

SELECT Employee_ID, Employee_Name,
       Attendance_Percentage,
       Days_Absent,
       Overtime_Hours,
       Net_Salary
FROM payroll
WHERE Attendance_Percentage < 80
ORDER BY Attendance_Percentage ASC;

SELECT
    ROUND(AVG(Attendance_Percentage), 2) AS mean_attendance,
    ROUND(AVG(Net_Salary), 2) AS mean_net_salary,
    ROUND(AVG(Overtime_Hours), 2) AS mean_overtime
FROM payroll;
