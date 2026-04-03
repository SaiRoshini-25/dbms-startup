# Software Requirements Specification

## Startup Incubator Management System

Version 1.0

---

## Chapter 1

## Introduction

This project is a prototype for a Startup Incubator Management System (SIMS), a database-backed web application designed to manage and streamline operations within a startup incubator ecosystem. The system is intended to handle interactions between incubator management, investors, startups, mentors, and other stakeholders involved in the incubation pipeline. This document provides an overview of the purpose, scope, intended audience, terminology, and conventions used throughout the specification.

### 1.1 Document Purpose

The purpose of this document is to provide a detailed and comprehensive analysis of the Startup Incubator Management System (SIMS). This Software Requirements Specification (SRS) captures both the functional and non-functional requirements needed to achieve the objectives of the product. The document also provides clarity on external interface requirements, use case models, and system constraints. It serves as the baseline for system design, development, testing, deployment, and maintenance.

### 1.2 Product Scope

The Startup Incubator Management System provides a centralized digital platform for the incubator to manage startups, investors, mentors, funding rounds, milestones, and associated operational records. The system replaces manual or fragmented data management practices and enables efficient coordination among all stakeholders. Key features include startup registration and tracking, investor portfolio management, mentor assignment, funding pipeline oversight, search, audit logging, and report generation. The system is designed to be scalable and adaptable to different incubator environments.

### 1.3 Intended Audience and Document Overview

The application is intended to be used by system administrators working in the startup incubator, investors, startup representatives, mentors, and incubator management.

The main categories of users are:

- Casual User: Incubator Management, which primarily views dashboards and reports
- Naive User: System Administrators, which manage data entry, validation, and updates
- Standalone User: Investors, startup representatives, directors, and mentors, which access modules relevant to their role

### 1.4 Definitions, Terms and Abbreviations

| S.No. | Term | Definition |
| --- | --- | --- |
| 1 | SIMS | Startup Incubator Management System |
| 2 | SRS | Software Requirements Specification |
| 3 | DBMS | Database Management System |
| 4 | Admin | System Administrator with full database access |
| 5 | Startup | An early-stage company enrolled in the incubator program |
| 6 | Investor | Individual or entity providing funding to startups |
| 7 | Mentor | Domain expert assigned to guide startups |
| 8 | KPI | Key Performance Indicator |
| 9 | MOU | Memorandum of Understanding |
| 10 | API | Application Programming Interface |

### 1.5 Document Conventions

This document follows the IEEE Std 830-1998 formatting style for Software Requirements Specifications. Functional requirements are labeled `F1`, `F2`, ..., `Fn`. Use cases are labeled `U1`, `U2`, ..., `Un`. All requirements use the word `shall` to indicate mandatory behavior.

### 1.6 References and Acknowledgments

- Fundamentals of Database Systems by Ramez Elmasri and Shamkant Navathe
- IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications
- IEEE SRS template: `http://www.cse.msu.edu/~cse870/IEEEXplore-SRS-template.pdf`

---

## Chapter 2

## Overall Description

### 2.1 Product Overview

The selected mini world for this project is that of a startup incubator. A business incubator is an organization that helps new startup companies develop by providing services, mentorship, operational support, and access to investors. The incubator works at both ends, with investors and with startups. The SIMS acts as the central data management platform for this incubator. It stores and manages data relating to startups, investors, mentors, funding rounds, milestones, activity logs, and system-generated reports. The system administrator acts as the super admin and has direct access to manage records in the database-backed application.

### 2.2 Product Functionality

The SIMS supports the following core functionalities:

- Startup representatives and investors can register into the system with relevant details
- Registered users can log in with valid credentials and access role-specific dashboards
- Startups can update their profiles, milestones, and funding requirements
- Investors can browse startup profiles, express interest, and manage their portfolios
- Administrators can assign mentors to startups and track engagement
- The system tracks funding rounds, MOU signing, and equity details
- The system generates progress reports and KPI dashboards for management

### 2.3 Design and Implementation Constraints

- All changes to startup profiles, investment deals, and mentor assignments must be reflected in real time in the database
- Financial data such as investment amounts must be stored with high precision
- The system must be accessible through a standard web browser with an internet connection
- Users must authenticate with valid credentials before accessing protected modules
- Stored data must comply with applicable data protection and privacy regulations

### 2.4 Assumptions and Dependencies

Assumptions:

- All startup, investor, and mentor data is stored in a relational database
- The system has sufficient storage and provides fast access to data
- The system is available 24/7 with minimal downtime
- Users have basic digital literacy and the interface is in English

Dependencies:

- The hardware and software described in Sections 3.1.2 and 3.1.3
- The system administrator has working knowledge of incubator operations
- The database is updated on every transaction, including registration, funding, mentor logging, milestone updates, and audit events

---

## Chapter 3

## Specific Requirements

### 3.1 External Interface Requirements

#### 3.1.1 User Interfaces

- The application opens to a login and registration page upon launch
- Role-based dashboards are shown after successful login for Admin, Investor, Startup Representative, and Mentor
- The interface uses a clean, minimal layout with intuitive navigation menus
- Colour schemes are chosen to be accessible and readable
- All forms include validation with descriptive error messages
- Search and filter functionality is available across major data views

#### 3.1.2 Hardware Interfaces

- Processor: Intel Core i3 or equivalent minimum
- Hard Disk: 100 GB or more
- RAM: 4 GB or more
- Network: Stable internet connection with minimum 1 Mbps

#### 3.1.3 Software Interfaces

| Software Used | Description |
| --- | --- |
| Operating System | Linux or Windows for broad deployment support and compatibility |
| Database | MySQL as the relational DBMS for SIMS |
| Backend Framework | Flask with Python for RESTful API development |
| Frontend | React.js with HTML and CSS for interactive UI |
| Version Control | Git and GitHub for collaborative development and version management |

### 3.2 Functional Requirements

- F1: The system shall allow a startup representative or investor to register into the system by providing their details. Registration data shall be stored in the database.
- F2: The system shall allow registered users to log in using valid credentials. Role-based access shall be enforced upon successful login.
- F3: The system shall deny access and display an error message `Invalid Credentials` if incorrect login details are provided.
- F4: The system shall allow administrators to add new startups to the incubator program with all relevant details, including name, domain, founding date, team size, and other profile information.
- F5: The system shall allow administrators to update startup profiles, including milestone completions, funding status, and team changes.
- F6: The system shall allow administrators to remove a startup from the system when it graduates or exits the program.
- F7: The system shall allow investors to view all registered startups and filter them by domain, funding stage, and performance metrics.
- F8: The system shall allow investors to express interest in a startup and initiate the investment discussion pipeline.
- F9: The system shall allow administrators to record and manage funding rounds including amount, equity percentage, investor details, and MOU status.
- F10: The system shall allow administrators to assign mentors to startups based on domain expertise.
- F11: The system shall allow mentors to view their assigned startups and log session notes and guidance records.
- F12: The system shall allow startups to view their mentor assignments, funding history, and milestone tracker.
- F13: The system shall allow administrators to generate progress reports for individual startups.
- F14: The system shall allow administrators to view the complete activity log and audit trail for all data changes.
- F15: The system shall allow investors to view their investment portfolio, including returns data and equity held across startups.
- F16: The system shall provide a search functionality for all entities, including startups, investors, and mentors, across the system.
- F17: The system shall enforce role-based access control so that users can only perform actions permitted for their role.

### 3.3 Use Case Model

#### 3.3.1 Login - U1

| Field | Value |
| --- | --- |
| Author | Member 1 |
| Purpose | To log in to the system with valid credentials |
| Requirements Traceability | F2, F3 |
| Priority | High |
| Preconditions | The user must have a registered account with valid credentials |
| Post Conditions | The user is successfully logged into their role-specific dashboard |
| Actors | Admin, Investor, Startup Representative, Mentor |
| Basic Flow | 1. User enters credentials. 2. System verifies. 3. User is redirected to dashboard. |
| Alternative Flow | User enters incorrect credentials. System shows `Invalid Credentials`. User is prompted to retry or register. |
| Exceptions | Account locked after repeated failed attempts |

#### 3.3.2 Register - U2

| Field | Value |
| --- | --- |
| Author | Member 1 |
| Purpose | To register a new user, either startup or investor, into the system |
| Requirements Traceability | F1 |
| Priority | High |
| Preconditions | The user must not already be registered in the system |
| Post Conditions | User account is created and credentials are stored in the database |
| Actors | Startup Representative, Investor |
| Basic Flow | 1. User fills registration form. 2. System validates input. 3. Account is created and stored. |
| Alternative Flow | If the user already exists, the system shows a message and redirects to login. |
| Exceptions | Submission of incomplete or invalid registration details |

#### 3.3.3 Add Startup - U3

| Field | Value |
| --- | --- |
| Author | Member 2 |
| Purpose | To add a new startup to the incubator program |
| Requirements Traceability | F4 |
| Priority | High |
| Preconditions | Admin must be logged in. Startup details must be complete and verified. |
| Post Conditions | Startup is added to the database and appears in the system |
| Actors | Admin |
| Basic Flow | 1. Admin fills in startup details. 2. System validates. 3. Startup record is created in the database. |
| Alternative Flow | If a startup with the same name already exists, the system alerts the admin. |
| Exceptions | Submission of incomplete mandatory fields |

#### 3.3.4 Update Startup Profile - U4

| Field | Value |
| --- | --- |
| Author | Member 2 |
| Purpose | To update the profile, milestones, or funding status of an existing startup |
| Requirements Traceability | F5 |
| Priority | High |
| Preconditions | Admin or Startup Representative must be logged in. Startup must exist in the system. |
| Post Conditions | Updated information is reflected in the database |
| Actors | Admin, Startup Representative |
| Basic Flow | 1. User selects startup profile. 2. Edits relevant fields. 3. System saves changes to the database. |
| Alternative Flow | If invalid data is entered, an inline validation message is shown. |
| Exceptions | Concurrent modification conflicts if two users edit the same record |

#### 3.3.5 Browse Startups - U5

| Field | Value |
| --- | --- |
| Author | Member 2 |
| Purpose | To allow investors to browse and filter startup profiles |
| Requirements Traceability | F7 |
| Priority | High |
| Preconditions | Investor must be logged in |
| Post Conditions | A filtered list of startups matching the investor's criteria is displayed |
| Actors | Investor |
| Basic Flow | 1. Investor opens startup directory. 2. Applies filters such as domain and stage. 3. Filtered results are displayed. |
| Alternative Flow | If no startups match the filter, a `No results found` message is shown. |
| Exceptions | Database connection failure |

#### 3.3.6 Express Interest - U6

| Field | Value |
| --- | --- |
| Author | Member 3 |
| Purpose | To allow an investor to express interest in a startup and initiate the investment pipeline |
| Requirements Traceability | F8 |
| Priority | Medium |
| Preconditions | Investor must be logged in. Target startup must exist in the system. |
| Post Conditions | Interest is logged and admin is notified for follow-up |
| Actors | Investor |
| Basic Flow | 1. Investor views startup profile. 2. Clicks `Express Interest`. 3. System logs the action and notifies admin. |
| Alternative Flow | If the investor already expressed interest, the system shows a notification that it is already recorded. |
| Exceptions | Investor expresses interest in a startup that has already closed its funding round |

#### 3.3.7 Record Funding Round - U7

| Field | Value |
| --- | --- |
| Author | Member 3 |
| Purpose | To record the details of a new funding round for a startup |
| Requirements Traceability | F9 |
| Priority | High |
| Preconditions | Admin must be logged in. Startup and investor must both be registered in the system. |
| Post Conditions | Funding round is recorded in the database and startup funding status is updated |
| Actors | Admin |
| Basic Flow | 1. Admin selects startup. 2. Admin enters funding details including amount, equity, investor, and MOU status. 3. System saves the record. |
| Alternative Flow | If equity percentage would make the total exceed 100%, the system shows a validation warning. |
| Exceptions | Duplicate funding round data for the same startup and investor |

#### 3.3.8 Assign Mentor - U8

| Field | Value |
| --- | --- |
| Author | Member 3 |
| Purpose | To assign a mentor to a startup for guidance and support |
| Requirements Traceability | F10 |
| Priority | Medium |
| Preconditions | Admin must be logged in. Both mentor and startup must be registered. |
| Post Conditions | Mentor assignment is stored in the database. Both mentor and startup are notified. |
| Actors | Admin |
| Basic Flow | 1. Admin selects startup. 2. Admin selects a mentor from the available list. 3. System creates the assignment and notifies both parties. |
| Alternative Flow | If the selected mentor is at maximum capacity, the system alerts the admin. |
| Exceptions | Attempt to assign a mentor who is already assigned to the same startup |

#### 3.3.9 Log Mentor Session - U9

| Field | Value |
| --- | --- |
| Author | Member 4 |
| Purpose | To allow a mentor to log session notes and record guidance provided to an assigned startup |
| Requirements Traceability | F11 |
| Priority | Medium |
| Preconditions | Mentor must be logged in. A startup must be assigned to the mentor. |
| Post Conditions | Session notes are stored in the database and visible to admin |
| Actors | Mentor |
| Basic Flow | 1. Mentor selects assigned startup. 2. Enters session date, topics covered, and notes. 3. System saves the log. |
| Alternative Flow | If no startups are assigned, the mentor sees an empty list with a prompt to contact admin. |
| Exceptions | Mentor logs a session for a startup that has been removed from the program |

#### 3.3.10 Generate Report - U10

| Field | Value |
| --- | --- |
| Author | Member 4 |
| Purpose | To generate progress reports for startups |
| Requirements Traceability | F13 |
| Priority | Medium |
| Preconditions | Admin must be logged in |
| Post Conditions | A report is generated and made available for download |
| Actors | Admin |
| Basic Flow | 1. Admin selects report type. 2. System compiles relevant data. 3. Report is displayed and offered for download as PDF or CSV. |
| Alternative Flow | If no data is available for the selected period, a `No data found` message is shown. |
| Exceptions | Admin requests a report for a startup that no longer exists in the system |

#### 3.3.11 View Portfolio - U11

| Field | Value |
| --- | --- |
| Author | Member 5 |
| Purpose | To allow an investor to view their investment portfolio |
| Requirements Traceability | F15 |
| Priority | Medium |
| Preconditions | Investor must be logged in |
| Post Conditions | Portfolio details including equity percentages and performance metrics are displayed |
| Actors | Investor |
| Basic Flow | 1. Investor navigates to Portfolio. 2. System fetches investment records. 3. Portfolio is displayed with aggregated statistics. |
| Alternative Flow | If no investments exist, a message prompts the investor to explore startups. |
| Exceptions | Portfolio contains data for a startup that has been archived |

---

## Chapter 4

## Other Non-Functional Requirements

### 4.1 Performance Requirements

- The system shall respond to user requests within 2 seconds under normal load
- Search queries across startup and investor records shall return results within 1 second
- The system shall support at least 200 concurrent users without major degradation in performance
- The database shall handle growth in records over a 5-year period without architectural redesign

### 4.2 Safety and Security Requirements

- All sensitive financial and personal data shall be encrypted in transit and protected at rest using standard industry practices
- Role-based access control shall be strictly enforced so that users can only access data relevant to their role
- Regular automated database backups shall be performed

### 4.3 Software Quality Attributes

#### 4.3.1 Reliability

- The system shall target 99% uptime
- Failure recovery mechanisms shall reduce the chance of data loss during unexpected shutdowns

#### 4.3.2 Usability

- The interface shall be intuitive and usable without formal training for all user roles
- A help or documentation section should be accessible from every page

#### 4.3.3 Maintainability

- The codebase shall follow standard software engineering practices, including modularization and documentation, to allow easy maintenance and future enhancement

#### 4.3.4 Portability

- The system shall be deployable on standard server infrastructure
- The frontend shall be compatible with modern browsers including Chrome, Firefox, Safari, and Edge

#### 4.3.5 Scalability

- The system architecture shall support future horizontal or service-level scaling as the number of startups, investors, and transactions grows

---

## Appendix A - Data Dictionary

| Term | Description |
| --- | --- |
| Admin / System Administrator | Super user with full CRUD access to all entities in the database and application |
| Startup | An early-stage company enrolled in the incubator program with team details, domain, milestones, and funding history |
| Investor | An individual or entity that provides financial capital to startups and can interact with the startup pipeline |
| Mentor | A domain expert assigned to provide guidance and advisory support to one or more startups |
| Funding Round | A structured investment event in which an investor provides capital to a startup in exchange for equity or equivalent investment terms |
| Milestone | A defined goal or achievement target used to track startup progress within the incubator |
| MOU | Memorandum of Understanding, a formal agreement outlining terms of engagement |
| KPI | Key Performance Indicator, a measurable value used to evaluate startup progress |
| Portfolio | The collection of startups in which an investor has invested, shown in the investor dashboard |
