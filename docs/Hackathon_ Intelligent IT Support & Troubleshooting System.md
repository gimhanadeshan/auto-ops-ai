# **Hackathon: Intelligent IT Support & Troubleshooting System**

**Background**

Modern organizations depend on a wide variety of digital systems—cloud services, internal applications, laptops, networks, communication tools, and on-premise infrastructure.

IT teams must constantly handle **two types of issues**:

### **1\. User-Reported Complaints**

Examples:

* “I can’t connect to VPN.”

* “My laptop is very slow.”

* “Android Studio keeps crashing.”

* “Printer not working.”

###  **2\. System-Generated Issues**

Examples:

* Server down

* High CPU / RAM

* Service not responding

* Backup failures

* Network connectivity errors

* Application crash logs

Today, support teams manually diagnose, run scripts, troubleshoot, and create tickets.  
Your challenge is to **build an intelligent system** that automates much of this workload **while maintaining strict privacy & safety**.

# **Challenge Goal**

Build an **AI-powered Intelligent IT Support System** that can:

- Detect system issues (optional but higher marks)  
- Handle user-reported complaints  
- Diagnose root causes  
- Run safe automated troubleshooting actions  
- Suggest fixes to users  
- Auto-resolve basic issues (if possible)  
- Create & update IT support tickets  
- Follow privacy, security, and access-control rules

This system **must** support user complaints. Handling system-generated issues is **optional**, but teams implementing it will receive **higher marks**.

# **Core Requirements**

## **1\. User-Reported Issue Handling**

Users should be able to submit issues through:

* Chat bot (Teams / Slack / JIRA / custom chat UI)

* Web form (custom UI, Google Form, etc.) (optional)

* Email (optional)

* Voice input (optional)

### **Examples**

* “My PC is very slow.”

* “Cannot log into VPN.”

* “VS Code is not opening.”

* “Wi-Fi disconnects often.”

### **Expected Behavior**

* Understand the user’s complaint

* Ask clarifying questions if needed

* Perform safe troubleshooting

* Provide clear step-by-step guidance

* Auto-update the ticket with progress and status

* Escalate to a human when needed

**2\. System Issue Detection (Optional)**

Your system should detect issues based on logs, signals, or mock monitoring data.

### **Examples**

* High CPU or RAM usage

* Low disk space

* Application crash logs

* Service not responding

* Database connection failures

* Network issues

### **Expected Behavior**

* Automatically create a case/ticket

* Provide possible root cause

* Recommend or run allowed troubleshooting actions

* Decide when human escalation is needed

* Log all actions for transparency

## **3\. Automated Troubleshooting Actions (Safe Mode Only)**

Your system may run **predefined safe troubleshooting operations** such as:

* Restarting a local application (mock / optional)

* Clearing cache/temp files

* Checking network adapters

* Running speed check

* Flushing DNS

* Checking disk space or disk health

* Killing a stuck process (mock or optional)

* Restarting a service (mock or optional)

### **Important Rules**

* No destructive OS commands

* All actions must be simulated or sandboxed, or secure way

* The system must **tell the user before executing**

* Ask for confirmation when required

### **Note:**

**Full “automated self-repair mode” is optional — teams that implement additional automated troubleshooting will receive higher marks, but the MVP only needs safe suggestions \+ simulated actions.**

## **4\. Ticketing System Integration**

Your system must maintain a **ticket lifecycle**.

A ticket should store:

* Issue type (system or user)

* Source of detection

* Summary of logs or complaint

* Automated troubleshooting attempts

* Current status:

  * Open

  * In-progress

  * Resolved

  * Escalated (human required)

* Assigned technician (if applicable) (can be AI or human)

A simple:

* mock database

* JSON storage

    
    
    
    
  

# **Privacy & Security Requirements**

Teams **must** follow the rules below.

## **1\. Data Safety**

* DO NOT collect personal data unless required for the issue

* Logs must be anonymized

* Credentials must NOT be stored or used

* Only synthetic or mock logs allowed

## **2\. Safe Execution**

* All automated commands must be sandboxed

* No destructive operations (delete, format, chmod, modify system files)

* No access to real OS-level privileged operations

* Simulated scripts are acceptable

## **3\. Access Control**

* System must restrict admin-only actions

* Unauthorized users must NOT access troubleshooting operations

* All automated actions must be recorded in an audit log

## **4\. Transparency**

* The system must **explain** what it will do

* Ask for approval before doing anything

* Provide a summary after each action

# **Evaluation Criteria**

| Category | Description |
| ----- | ----- |
| **Innovation** | Creativity, problem approach, intelligent logic |
| **Technical Depth** | Quality of architecture, algorithms, integrations |
| **Accuracy** | Correctness of problem detection and suggestions |
| **Safety** | Strict adherence to privacy & safe-execution rules |
| **User Experience** | Clarity of communication and ease of use |
| **Completeness** | Handling both system & user issues properly |
| **Presentation** | Demo clarity, stability, documentation quality |

# **Minimum Deliverables**

Teams must submit:

### **A working prototype**

(Web app, dashboard, CLI tool, chatbot, or hybrid)

### **Architecture diagram**

* Components

* Safety layers

### **List of supported system issues**

And how each is detected and handled.

### **Sample logs**

Used for system-signal based issue detection.

### **Documentation including:**

* How the system works

* Automated/simulated actions used

* Safety rules followed

* Limitations & future improvements

# **Bonus Features (Optional – Higher Score)**

These are NOT required but will give extra marks:

* Predictive issue detection (based on patterns)

* Slack/Teams integration

* Smart escalation logic

* Voice-based issue reporting

* Notifications (email/SMS/push)

* Cross-platform troubleshooting (Win/Mac/Linux)

* AI-generated system health reports

