DROP SCHEMA IF EXISTS lab CASCADE;
CREATE SCHEMA lab;
CREATE TABLE lab.departments(id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL, budget NUMERIC(12,2) DEFAULT 0, location TEXT);
CREATE TABLE lab.employees(
  id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  salary NUMERIC(10,2) NOT NULL CHECK (salary > 0),
  department_id INT REFERENCES lab.departments(id), manager_id INT REFERENCES lab.employees(id),
  hire_date DATE NOT NULL, is_active BOOLEAN DEFAULT TRUE, skills JSONB DEFAULT '[]', bio TEXT);
CREATE TABLE lab.projects(id SERIAL PRIMARY KEY, name TEXT NOT NULL, department_id INT REFERENCES lab.departments(id),
  budget NUMERIC(12,2), start_date DATE, end_date DATE);
CREATE TABLE lab.assignments(employee_id INT REFERENCES lab.employees(id) ON DELETE CASCADE,
  project_id INT REFERENCES lab.projects(id) ON DELETE CASCADE, hours INT DEFAULT 0, role TEXT,
  PRIMARY KEY(employee_id, project_id));
INSERT INTO lab.departments(name,budget,location) VALUES
 ('Engineering',900000,'Chennai'),('Sales',400000,'Mumbai'),('HR',150000,'Chennai'),('Finance',300000,'Delhi'),('Legal',120000,'Delhi');
INSERT INTO lab.employees(name,email,salary,department_id,manager_id,hire_date,skills) VALUES
 ('Asha Rao','asha@acme.com',250000,1,NULL,'2015-03-01','["python","leadership"]'),
 ('Ravi Kumar','ravi@acme.com',180000,1,1,'2017-06-15','["python","sql","aws"]'),
 ('Meena Iyer','meena@acme.com',150000,1,2,'2019-01-10','["react","typescript"]'),
 ('Karthik S','karthik@acme.com',140000,1,2,'2020-08-20','["python","docker"]'),
 ('Divya N','divya@acme.com',120000,2,1,'2018-04-02','["negotiation"]'),
 ('Arjun P','arjun@acme.com',90000,2,5,'2021-02-11','["crm"]'),
 ('Sneha M','sneha@acme.com',85000,2,5,'2022-07-19','["crm","excel"]'),
 ('Lakshmi R','lakshmi@acme.com',95000,3,1,'2016-11-30','["recruiting"]'),
 ('Vikram T','vikram@acme.com',110000,4,1,'2019-09-09','["excel","sql"]'),
 ('Priya K','priya@acme.com',105000,4,9,'2023-01-16','["sql","accounting"]'),
 ('Naveen B','naveen@acme.com',130000,1,2,'2021-10-05','["go","kubernetes"]'),
 ('Isha G','isha@acme.com',80000,NULL,8,'2024-03-04','[]');
INSERT INTO lab.projects(name,department_id,budget,start_date,end_date) VALUES
 ('Atlas',1,500000,'2024-01-01','2024-12-31'),('Beacon',1,300000,'2024-03-01',NULL),
 ('Compass',2,150000,'2023-06-01','2024-05-31'),('Dynamo',4,90000,'2024-02-01',NULL),('Echo',NULL,50000,'2025-01-01',NULL);
INSERT INTO lab.assignments(employee_id,project_id,hours,role) VALUES
 (2,1,120,'lead'),(3,1,200,'dev'),(4,1,180,'dev'),(11,2,160,'dev'),(2,2,40,'advisor'),(4,2,60,'dev'),
 (5,3,100,'lead'),(6,3,150,'analyst'),(7,3,130,'analyst'),(9,4,90,'lead'),(10,4,110,'analyst');
