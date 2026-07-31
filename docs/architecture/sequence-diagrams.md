# Sequence Diagrams

## 1. Registration, email verification, and login

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Frontend (SPA)
    participant API as Django API
    participant Celery as Celery Worker
    participant DB as MySQL

    U->>FE: Fill registration form
    FE->>API: POST /auth/register/
    API->>DB: Create User (is_email_verified=False)
    API->>DB: Create EmailVerificationToken
    API->>Celery: send_verification_email.delay()
    Celery-->>U: Verification email
    API-->>FE: 201 Created

    U->>FE: Clicks verification link
    FE->>API: POST /auth/verify-email/ {token}
    API->>DB: Validate token, set is_email_verified=True
    API-->>FE: 200 OK

    U->>FE: Enter email + password
    FE->>API: POST /auth/login/
    API->>DB: Check credentials, lockout status
    alt valid credentials
        API->>DB: Reset failed_login_attempts, create UserSession
        API->>DB: Write AuditLog(login_success)
        API-->>FE: 200 {access, refresh, user}
        FE->>FE: Store tokens (localStorage)
    else invalid credentials
        API->>DB: Increment failed_login_attempts (lock if threshold hit)
        API->>DB: Write AuditLog(login_failed)
        API-->>FE: 401 Unauthorized
    end
```

## 2. Journal entry → AI analysis → risk detection → notification

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Frontend
    participant API as Django API
    participant Q as Celery (analyze_content)
    participant AI as AI Services
    participant DB as MySQL

    U->>FE: Write and submit journal entry
    FE->>API: POST /journals/
    API->>DB: Create JournalEntry
    API->>Q: analyze_content.delay("journals", "journalentry", id)
    API-->>FE: 201 Created (immediate — analysis is async)

    Q->>AI: analyze_sentiment(text)
    AI-->>Q: sentiment, stress/anxiety/burnout/depression scores, keywords
    Q->>DB: Create SentimentResult

    Q->>AI: analyze_emotion(text)
    AI-->>Q: dominant_emotion, per-emotion scores
    Q->>DB: Create EmotionResult

    Q->>AI: detect_crisis_risk(text)
    alt crisis phrase matched
        AI-->>Q: risk_level, triggered_phrases
        Q->>DB: Create RiskAssessment
        Q->>DB: JournalEntry.is_flagged = True
        Q->>DB: Create Notification (in-app, risk_alert)
        Q->>DB: Write AuditLog(risk_detected)
    end

    Q->>Q: recompute_wellness_score.delay(user_id, entry_date)
```

## 3. Assessment submission with crisis flag (PHQ-9 item 9)

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Frontend
    participant API as Django API
    participant DB as MySQL

    U->>FE: Complete PHQ-9 questionnaire
    FE->>API: POST /assessments/submit/ {answers[]}
    API->>API: Validate all questions answered
    API->>API: total_score = sum(answers)
    API->>API: score_assessment() → severity, interpretation
    API->>DB: Create AssessmentResult + AssessmentAnswer rows

    alt item 9 answer > 0
        API->>DB: Create RiskAssessment (detection_source=assessment)
        API->>DB: Query EmergencyResource by user's country
        API-->>FE: 201 {..., risk_flag: true, crisis_resources: [...]}
        FE->>FE: Show crisis resources inline immediately
    else item 9 answer == 0
        API-->>FE: 201 {..., risk_flag: false}
    end

    API->>API: recompute_wellness_score.delay(), generate_recommendations_for_user.delay()
```

## 4. Appointment booking and admin approval

```mermaid
sequenceDiagram
    actor U as User
    actor A as Admin
    participant FE as Frontend
    participant API as Django API
    participant DB as MySQL

    U->>FE: Select counselor + time, submit
    FE->>API: POST /appointments/
    API->>DB: Check counselor.is_accepting_appointments
    API->>DB: Check for overlapping appointment (conflict check)
    alt available
        API->>DB: Create Appointment (status=pending)
        API-->>FE: 201 Created
    else conflict
        API-->>FE: 400 Bad Request
    end

    A->>FE: Open Admin → Appointments
    FE->>API: GET /appointments/admin/list/?status=pending
    API-->>FE: List of pending appointments

    A->>FE: Approve appointment
    FE->>API: POST /appointments/admin/{id}/approve/
    API->>DB: status=approved, approved_by=admin
    API->>DB: Write AdminActionLog
    API-->>FE: 200 OK
```

## 5. LibreChat SSO and conversation sync

See [librechat-integration.md](librechat-integration.md) for the full SSO
sequence diagram and the conversation-sync flow.
