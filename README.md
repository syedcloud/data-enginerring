# Data Engineering
# 🚀 Spark and SQL Interview Scenario Questions

---

## 📚 Table of Contents

| No | Scenarios                   |
| -- | --------------------------- |
| 1  | [Scenario-1](#scenario-1)   |
| 2  | [Scenario-2](#scenario-2)   |



---

## Scenario-1

👉 


### ❓ Problem Statement

You are given two datasets:

* **Employee table** → contains employee `id` and `name`
* **Salary table** → contains `id` and `salary`

Some employees do not have salary records.

👉 Requirement:

* Perform a **left join**
* Replace missing salaries (`NULL`) with **0**



### 📊 Input Data

**Employee Data**

| id | name  |
| -- | ----- |
| 1  | Henry |
| 2  | Smith |
| 3  | Hall  |

**Salary Data**

| id | salary |
| -- | ------ |
| 1  | 100    |
| 2  | 500    |
| 4  | 1000   |


### ✅ Output

| id | name  | salary |
| -- | ----- | ------ |
| 1  | Henry | 100    |
| 2  | Smith | 500    |
| 3  | Hall  | 0      |



### 🔥 Interview Follow-up Questions

1. What is the difference between **inner join and left join**?
2. How does Spark handle **NULL values** in joins?
3. Can you replace NULL values using `fillna()` instead?
4. What happens if there are **duplicate IDs**?

---
## Scenario-2
👉 

### ❓ Problem Statement

You are given match results between teams:

* `TeamA` vs `TeamB`
* Column `Won` indicates the winning team

👉 Requirement:

* Find **total wins for each team**
* Include teams with **zero wins**
* Sort results by team name



### 📊 Input Data

| TeamA | TeamB | Won |
| ----- | ----- | --- |
| A     | D     | D   |
| B     | A     | A   |
| A     | D     | A   |


### ✅ Output

| TeamName | won |
| -------- | --- |
| A        | 2   |
| B        | 0   |
| D        | 1   |



### 🔥 Interview Follow-up Questions

1. Why do we use **UNION + DISTINCT** here?
2. What happens if we use **INNER JOIN instead of LEFT JOIN**?
3. Can we solve this using **window functions**?
4. How would you calculate **losses** or **win percentage**?







### 🎯 Key Concepts Tested

* Aggregations in Spark
* UNION and DISTINCT
* LEFT JOIN
* NULL handling (`fillna`)
* Data transformation logic




---

## Scenario-3

👉 Add your content here

---

## Scenario-4

👉 Add your content here

---

## Scenario-5

👉 Add your content here

---

## Scenario-6

👉 Add your content here

---

## Scenario-7

👉 Add your content here

---

## Scenario-8

👉 Add your content here

---

## Scenario-9

👉 Add your content here

---

## Scenario-10

👉 Add your content here

---

## Scenario-11

👉 Add your content here

---

## Scenario-12

👉 Add your content here

---

## Scenario-13

👉 Add your content here

---

## Scenario-14

👉 Add your content here
