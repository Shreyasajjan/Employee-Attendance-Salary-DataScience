PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS payroll;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    Employee_ID TEXT PRIMARY KEY,
    Employee_Name TEXT NOT NULL,
    Gender TEXT,
    Age INTEGER CHECK (Age >= 18),
    Department TEXT NOT NULL,
    Job_Role TEXT NOT NULL,
    Joining_Date TEXT NOT NULL,
    Monthly_Salary REAL NOT NULL CHECK (Monthly_Salary >= 0),
    Employment_Type TEXT,
    Location TEXT
);

CREATE TABLE attendance (
    Attendance_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Employee_ID TEXT NOT NULL,
    Attendance_Status TEXT NOT NULL CHECK (
        Attendance_Status IN ('Present', 'Late', 'Absent', 'Leave', 'Holiday')
    ),
    Check_In TEXT,
    Check_Out TEXT,
    Work_Hours REAL NOT NULL CHECK (Work_Hours >= 0),
    Overtime_Hours REAL NOT NULL CHECK (Overtime_Hours >= 0),
    Leave_Type TEXT,
    Late_Minutes REAL NOT NULL CHECK (Late_Minutes >= 0),
    UNIQUE(Date, Employee_ID),
    FOREIGN KEY (Employee_ID) REFERENCES employees(Employee_ID)
);

CREATE TABLE payroll (
    Payroll_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Employee_ID TEXT NOT NULL,
    Employee_Name TEXT NOT NULL,
    Department TEXT NOT NULL,
    Job_Role TEXT NOT NULL,
    Monthly_Salary REAL NOT NULL CHECK (Monthly_Salary >= 0),
    Working_Days INTEGER NOT NULL,
    Days_Present INTEGER NOT NULL,
    Days_Absent INTEGER NOT NULL,
    Days_On_Leave INTEGER NOT NULL,
    Attendance_Percentage REAL NOT NULL CHECK (Attendance_Percentage BETWEEN 0 AND 100),
    Total_Work_Hours REAL NOT NULL,
    Overtime_Hours REAL NOT NULL,
    Overtime_Pay REAL NOT NULL,
    Attendance_Bonus REAL NOT NULL,
    Basic_Pay REAL NOT NULL,
    Gross_Salary REAL NOT NULL,
    PF_Deduction REAL NOT NULL,
    Tax_Deduction REAL NOT NULL,
    Other_Deductions REAL NOT NULL,
    Net_Salary REAL NOT NULL CHECK (Net_Salary >= 0),
    FOREIGN KEY (Employee_ID) REFERENCES employees(Employee_ID)
);
