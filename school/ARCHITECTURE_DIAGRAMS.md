# System Architecture & Data Flow Diagrams

## Academic Hierarchy

```
┌──────────────────────────────────────────────────────────┐
│                      INSTITUTION                         │
└───────────────────────────┬────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────┐        ┌────▼────┐       ┌────▼────┐
    │  Dept 1 │        │  Dept 2 │       │  Dept 3 │
    │   (CS)  │        │ (ENGR)  │       │ (MATHS) │
    └────┬────┘        └────┬────┘       └────┬────┘
         │                  │                  │
    ┌────┴──────┬──────┐   │                  │
    │            │      │   │                  │
┌───▼──┐  ┌─────▼──┐ ┌─┴──▼──┐              │
│CS101 │  │ CS202  │ │ENG101 │ ◄─────────────┘
│Prog  │  │ DB     │ │Mechan │
└───┬──┘  └─┬──────┘ └───────┘
    │       │
    │   ┌───▼──────┬─────────┬──────────┐
    │   │           │         │          │
 ┌──┴───▼──┐  ┌────▼──┐  ┌──▼───┐  ┌──▼──┐
 │CS101-U1 │  │CS101-│  │CS101 │  │CS101│
 │ Sem 1   │  │U2    │  │-U3   │  │-U4  │
 │Python   │  │Sem 2 │  │Sem 3 │  │Sem 4│
 │5 Credits│  │      │  │      │  │     │
 └────┬────┘  └──────┘  └──────┘  └─────┘
      │
 ┌────▼──────────────────────────────┐
 │  REPORTING SESSION: 2024/2025 S1  │
 │  - Start: Jan 2024                │
 │  - End: Apr 2024                  │
 │  - Semester: 1                    │
 └────┬──────────────────────────────┘
      │
 ┌────▼────────────────────────────────┐
 │     ENROLLMENT (50 students)        │
 │  - Course: CS101                    │
 │  - Session: 2024/2025 S1            │
 │  - Status: Active                   │
 │  - Students: STU001-STU050          │
 └────┬────────────────────────────────┘
      │
 ┌────▼──────────────────────────────┐
 │    RESULT (Per Student)            │
 │  - CA Score: 35/40                 │
 │  - Exam: 55/60                     │
 │  - Total: 90/100                   │
 │  - Grade: A+                       │
 │  - Points: 4.0                     │
 │  - Pass: Yes                       │
 └───────────────────────────────────┘
```

---

## Student Registration Flow

```
START
  │
  ▼
┌─────────────────────────────┐
│  LOGIN                      │
│  Username: student_id       │
│  Password: ****             │
└────┬────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Go to: /school/register/     │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Check Active Session         │
│ - Status: ACTIVE?            │
│ - Today >= Start Date?       │
│ - Today <= End Date?         │
└────┬─────────────────────────┘
     │ YES
     ▼
┌──────────────────────────────┐
│ Show Available Courses       │
│ - Filter by department       │
│ - Only active courses        │
│ - Hide already enrolled      │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Student Selects Courses      │
│ - Multiple checkboxes        │
│ - Show prerequisites         │
│ - Show credit hours          │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Confirm Registration         │
│ - Review selected courses    │
│ - Show total credits         │
│ - Submit button              │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ CREATE ENROLLMENTS           │
│ For each selected course:    │
│  - New Enrollment record     │
│  - Status: "active"          │
│  - Session: Current          │
│  - Date: Today               │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ SUCCESS MESSAGE              │
│ Enrolled in 4 courses        │
│ Total Credits: 12            │
└────┬─────────────────────────┘
     │
     ▼
  VIEW PROFILE
     │
     ▼
  (Show Enrollments)
     │
     ▼
  END
```

---

## Admin Bulk Mark Upload Flow

```
START
  │
  ▼
┌──────────────────────────────┐
│  LOGIN (ADMIN)               │
│  Staff/Superuser Required    │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Go to: /school/results/      │
│        bulk-upload/          │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ SELECT COURSE                │
│ - Dropdown list              │
│ - Active courses only        │
│ - Show course code           │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ SELECT SESSION               │
│ - Dropdown list              │
│ - Active sessions only       │
│ - Show date range            │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ FETCH ENROLLMENTS            │
│ Query:                       │
│  course = selected           │
│  session = selected          │
│  status = "active"           │
│ Result: List of students     │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ DISPLAY SCORE FORM           │
│                              │
│ For each enrollment:         │
│ ┌──────────────────────┐    │
│ │STU001 John Smith     │    │
│ │CA Score: [__/40]     │    │
│ │Exam Score: [__/60]   │    │
│ └──────────────────────┘    │
│                              │
│ ┌──────────────────────┐    │
│ │STU002 Jane Doe       │    │
│ │CA Score: [__/40]     │    │
│ │Exam Score: [__/60]   │    │
│ └──────────────────────┘    │
│                              │
│ ... (50 more students) ...   │
│                              │
│ [UPLOAD RESULTS]             │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ FOR EACH STUDENT:            │
│                              │
│ ca_score = form input        │
│ exam_score = form input      │
│                              │
│ Get/Create Result object     │
│ result.ca = ca_score         │
│ result.exam = exam_score     │
│ result.save()  ◄──────────┐  │
│                            │  │
│                 (Auto calc)│  │
│                 total = ca │  │
│                     + exam │  │
│                 grade = ... │  │
│                 points = .. │  │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ SUCCESS NOTIFICATION         │
│ Updated 47 results           │
│ Course: CS101                │
│ Session: 2024/2025-1         │
└────┬─────────────────────────┘
     │
     ▼
  REDIRECT to results_list
     │
     ▼
  END
```

---

## Grade Calculation Logic

```
┌───────────────────────────────────┐
│  INPUT SCORES                     │
│  CA Score: 0-40 (entered by admin)│
│  Exam Score: 0-60 (entered admin) │
└────┬────────────────────────────┘
     │
     ▼
┌───────────────────────────────────┐
│  CALCULATE TOTAL                  │
│  total = CA + Exam                │
│  (Range: 0-100)                   │
└────┬────────────────────────────┘
     │
     ▼
┌───────────────────────────────────┐
│  ASSIGN GRADE                     │
│                                   │
│  if total >= 90: grade = 'A+'     │
│  elif total >= 80: grade = 'A'    │
│  elif total >= 70: grade = 'B+'   │
│  elif total >= 60: grade = 'B'    │
│  elif total >= 50: grade = 'C+'   │
│  elif total >= 40: grade = 'C'    │
│  elif total >= 30: grade = 'D'    │
│  else: grade = 'F'                │
└────┬────────────────────────────┘
     │
     ▼
┌───────────────────────────────────┐
│  ASSIGN GRADE POINTS              │
│                                   │
│  A+  → 4.0 points                 │
│  A   → 3.9 points                 │
│  B+  → 3.7 points                 │
│  B   → 3.0 points                 │
│  C+  → 2.3 points                 │
│  C   → 2.0 points                 │
│  D   → 1.0 points                 │
│  F   → 0.0 points                 │
└────┬────────────────────────────┘
     │
     ▼
┌───────────────────────────────────┐
│  DETERMINE PASS/FAIL              │
│                                   │
│  if total >= 40:                  │
│    is_pass = True (PASS)          │
│  else:                            │
│    is_pass = False (FAIL)         │
└────┬────────────────────────────┘
     │
     ▼
┌───────────────────────────────────┐
│  SAVE RESULT                      │
│  - total_score                    │
│  - grade                          │
│  - grade_point                    │
│  - is_pass                        │
│  - recorded_date (now)            │
└────┬────────────────────────────┘
     │
     ▼
   OUTPUT
     │
     ▼
┌───────────────────────────────────┐
│  RESULT RECORD CREATED            │
│  Status: COMPLETE                 │
│  Ready for GPA calculation        │
└───────────────────────────────────┘
```

---

## GPA Calculation

```
┌─────────────────────────────────────┐
│  FETCH ALL RESULTS FOR STUDENT      │
│  - Course 1: Grade 4.0              │
│  - Course 2: Grade 3.7              │
│  - Course 3: Grade 3.0              │
│  - Course 4: Grade 2.3              │
│  Total: 4 courses                   │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  CALCULATE GPA                      │
│                                     │
│  total_points = 4.0 + 3.7 + 3.0     │
│                + 2.3                │
│              = 13.0                 │
│                                     │
│  num_courses = 4                    │
│                                     │
│  GPA = total_points / num_courses   │
│  GPA = 13.0 / 4                     │
│  GPA = 3.25                         │
│                                     │
│  Round to 2 decimals: 3.25          │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  DISPLAY TO STUDENT                 │
│                                     │
│  Current GPA: 3.25 / 4.0            │
│  Performance: Excellent             │
│  Courses Completed: 4               │
│  Average Grade: B+                  │
└─────────────────────────────────────┘
```

---

## Database Schema (Simplified)

```
COURSE_UNIT
├─ id (PK)
├─ course_id (FK) → COURSE
├─ session_id (FK) → REPORTING_SESSION
├─ title
├─ code (UNIQUE)
├─ credits
├─ semester (1/2/3)
├─ instructor
└─ is_active

ENROLLMENT
├─ id (PK)
├─ student_id (FK) → STUDENT
├─ course_id (FK) → COURSE
├─ session_id (FK) → REPORTING_SESSION
├─ enrollment_date
├─ status (active/completed/dropped)
└─ created_at

RESULT
├─ id (PK)
├─ student_id (FK) → STUDENT
├─ course_id (FK) → COURSE
├─ session_id (FK) → REPORTING_SESSION
├─ continuous_assessment (0-40)
├─ exam_score (0-60)
├─ total_score (0-100) [CALCULATED]
├─ grade (A+/A/B+/B/C+/C/D/F) [CALCULATED]
├─ grade_point (4.0-0.0) [CALCULATED]
├─ is_pass (True/False) [CALCULATED]
└─ recorded_date
```

---

## User Roles & Permissions

```
┌──────────────────────────┐
│      USER ROLES          │
└──────────────────────────┘

ANONYMOUS USER
├─ Can view: Dashboard (limited)
├─ Cannot: Access any forms
└─ Can: Login

STUDENT USER
├─ Can view: Own profile, own results, own GPA
├─ Can do: Self-register for courses
├─ Cannot: Edit marks, create units, enroll others
└─ LoginRequiredMixin: Required

ADMIN USER (Staff)
├─ Can view: Everything
├─ Can do: CRUD all objects
├─ Can: Upload marks (bulk/single)
├─ Can: Create/edit/delete units
├─ Can: Bulk enroll students
├─ Can: Manage all data
└─ AdminRequiredMixin: Required
   (is_staff or is_superuser)
```

---

## Error Handling Flow

```
┌──────────────────────────────┐
│  USER SUBMITS FORM           │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│  VALIDATE DATA               │
│  - Required fields?          │
│  - Data type correct?        │
│  - Unique constraints?       │
│  - Range validation?         │
└────┬─────────────────────────┘
     │
     ├─ INVALID ────┐
     │              │
     │         ┌────▼──────────┐
     │         │ Show errors   │
     │         │ Highlight bad │
     │         │ fields        │
     │         │ Reload form   │
     │         └───────────────┘
     │
     │ VALID
     ▼
┌──────────────────────────────┐
│  CHECK PERMISSIONS           │
│  - User is_staff?            │
│  - User is_superuser?        │
│  - User owns this resource?  │
└────┬─────────────────────────┘
     │
     ├─ FORBIDDEN ──┐
     │              │
     │         ┌────▼──────────┐
     │         │ Error page    │
     │         │ Permission    │
     │         │ denied        │
     │         │ Redirect      │
     │         └───────────────┘
     │
     │ ALLOWED
     ▼
┌──────────────────────────────┐
│  SAVE TO DATABASE            │
│  - Try save()                │
└────┬─────────────────────────┘
     │
     ├─ ERROR ──────┐
     │              │
     │         ┌────▼──────────┐
     │         │ Log error     │
     │         │ Show message  │
     │         │ Reload form   │
     │         └───────────────┘
     │
     │ SUCCESS
     ▼
┌──────────────────────────────┐
│  SHOW SUCCESS MESSAGE        │
│  Redirect to list/detail     │
└──────────────────────────────┘
```

---

## System Status Indicators

```
SESSION STATUS
├─ UPCOMING
│  └─ Start date > today
│     └─ Color: Yellow
│     └─ Action: Cannot register yet
│
├─ ACTIVE
│  └─ Start date <= today <= end date
│     └─ Color: Green
│     └─ Action: Can register/upload marks
│
└─ CLOSED
   └─ End date < today
      └─ Color: Red
      └─ Action: Read-only

ENROLLMENT STATUS
├─ ACTIVE
│  └─ Student is taking course
│  └─ Marks can be entered
│
├─ COMPLETED
│  └─ Course finished
│  └─ Final grade recorded
│
└─ DROPPED
   └─ Student withdrew
   └─ No marks recorded

PASS/FAIL
├─ PASS
│  └─ Total score >= 40
│  └─ Color: Green
│
└─ FAIL
   └─ Total score < 40
   └─ Color: Red
```

---

This visual documentation helps developers understand the system flow and relationships.
