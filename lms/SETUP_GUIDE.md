# LMS (Learning Management System) Setup Guide

## Features

### For Admins
- ✅ Create and manage exams
- ✅ Set exam marks (default 30 marks)
- ✅ Add multiple choice questions
- ✅ Set correct answers
- ✅ Configure exam scheduling and duration
- ✅ View student results and analytics
- ✅ Export exam reports

### For Students
- ✅ Browse available exams
- ✅ Take timed exams
- ✅ Answer multiple choice questions
- ✅ Submit exams
- ✅ View results and scores
- ✅ Review correct answers
- ✅ View exam history

## Quick Start

### 1. Run Migrations

```bash
python manage.py makemigrations lms
python manage.py migrate lms
```

### 2. Access Admin Panel

Navigate to `http://localhost:8000/admin/`

Go to **LMS** section to:
- Create exams
- Add questions
- Add answer choices
- Review student results

### 3. Create Your First Exam

1. **Admin Dashboard**: `http://localhost:8000/lms/admin/dashboard/`
2. Click **"Create Exam"**
3. Fill in exam details:
   - Title: "Python Basics Quiz"
   - Total Marks: 30
   - Passing Marks: 15
   - Duration: 60 minutes
   - Status: Published
   - Start & End times

4. Click **"Save Changes"**

### 4. Add Questions

1. From exam detail page, click **"Add Question"**
2. Enter question text
3. Set marks (e.g., 1 mark per question)
4. Click **"Save Question"**
5. Click **"Add Answer Choices"**
6. Enter 4 answer choices
7. **Mark the correct answer** by checking the checkbox
8. Click **"Save Choices"**

Repeat for each question.

### 5. Students Take Exam

1. Navigate to `http://localhost:8000/lms/exams/`
2. Click **"Start Exam"** on an available exam
3. Read instructions and confirm
4. Answer all questions (multiple choice)
5. Click **"Submit Exam"**
6. View results and answer review

## URL Routes

### Admin Routes
| Route | Purpose |
|-------|---------|
| `/lms/admin/dashboard/` | Admin dashboard |
| `/lms/admin/create-exam/` | Create new exam |
| `/lms/admin/exam/<id>/edit/` | Edit exam |
| `/lms/admin/exam/<id>/detail/` | View exam details |
| `/lms/admin/exam/<id>/results/` | View all results |
| `/lms/admin/attempt/<id>/details/` | Student's detailed results |

### Student Routes
| Route | Purpose |
|-------|---------|
| `/lms/exams/` | List available exams |
| `/lms/exam/<id>/instructions/` | Exam instructions |
| `/lms/attempt/<id>/take/` | Take exam |
| `/lms/attempt/<id>/result/` | View result |
| `/lms/my-exams/` | Exam history |

## Admin Features

### Create Exam
```
Title: "Python Fundamentals"
Description: "Test your Python knowledge"
Total Marks: 30
Passing Marks: 15
Duration: 60 minutes
Status: Published
Schedule:
  - Start: 2025-01-25 09:00:00
  - End: 2025-01-25 17:00:00
```

### Questions
- Add multiple questions (5 for 30-mark exam, 1 mark each)
- Each question can have 2-4 choices
- Mark exactly one choice as correct
- Add explanations for learning

### Results Dashboard
- View all student attempts
- See scores and percentages
- Check pass/fail status
- Review individual answers
- Download reports

## Student Features

### Taking an Exam
1. Click "Start Exam"
2. Read instructions
3. Answer questions (one at a time)
4. Question navigator sidebar shows progress
5. Submit when done
6. Cannot change answers after submission

### Reviewing Results
- See final score and percentage
- View each question and correct answer
- Read explanations if provided
- Check if you passed/failed
- Compare with passing marks

### Exam History
- View all attempted exams
- See scores and results
- Retake exams if available
- Track performance

## Data Models

### Exam
- Title, description
- Total marks (default 30)
- Passing marks
- Duration in minutes
- Status (draft, published, closed)
- Scheduling (start_time, end_time)
- Settings (show answers, allow review, shuffle questions)
- Created by admin user

### Question
- Exam foreign key
- Question text
- Difficulty (easy, medium, hard)
- Marks allocated
- Explanation
- Order in exam

### Choice
- Question foreign key
- Choice text
- Is correct (boolean)
- Order

### ExamAttempt
- Exam & Student foreign keys
- Status (in_progress, submitted, completed)
- Started, submitted, reviewed timestamps
- Obtained marks
- Percentage
- Pass/fail flag
- Review count

### StudentAnswer
- ExamAttempt & Question foreign keys
- Selected choice
- Timestamps

## Configuration

### Exam Settings
```python
EXAM_CONFIG = {
    'DEFAULT_MARKS': 30,  # Default total marks
    'DEFAULT_DURATION': 60,  # Minutes
    'SHOW_ANSWERS': True,  # Show correct answers after submission
    'ALLOW_REVIEW': True,  # Allow reviewing submitted exams
    'SHUFFLE_QUESTIONS': False,  # Randomize question order
}
```

### Scoring
- Each question has individual marks
- Total marks = sum of all question marks
- Passing % = (student marks / total marks) * 100
- Passing status = score >= passing marks

## Best Practices

1. **Question Design**
   - Clear, unambiguous questions
   - Relevant choices
   - One obvious correct answer
   - Provide explanations

2. **Exam Settings**
   - Set realistic duration
   - Appropriate passing marks
   - Enable answer review for learning
   - Publish well in advance

3. **Student Experience**
   - Clear instructions
   - Question navigator
   - Time remaining display
   - Immediate feedback

4. **Analysis**
   - Review question difficulty
   - Check pass rates
   - Identify weak areas
   - Adjust future exams

## Troubleshooting

### Issue: Can't see exams
**Solution**: Check exam status is "Published" and current time is within exam window

### Issue: Can't submit exam
**Solution**: Answer all questions before submission

### Issue: Answers not saving
**Solution**: Ensure JavaScript is enabled; check browser console for errors

### Issue: Wrong score calculation
**Solution**: Verify only ONE choice per question is marked correct

## Future Enhancements

- [ ] Negative marking
- [ ] Essay/short answer questions
- [ ] File upload questions
- [ ] Proctoring with video
- [ ] Question bank management
- [ ] Randomized exams from bank
- [ ] Grade distribution reports
- [ ] Certificate generation
- [ ] Mobile app
- [ ] Progress tracking
