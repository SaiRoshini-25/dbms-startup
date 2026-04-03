-- Startup Incubator Management System
-- SDD schema as source of truth, with minimal extension columns/tables required by the web app.

CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(30) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE permissions (
    permission_id INT PRIMARY KEY AUTO_INCREMENT,
    permission_code VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL
);

CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
);

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    organization_name VARCHAR(150),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE user_profiles (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    address_line VARCHAR(255),
    city VARCHAR(100),
    state_name VARCHAR(100),
    country_name VARCHAR(100),
    postal_code VARCHAR(20),
    linkedin_url VARCHAR(255),
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE startups (
    startup_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_name VARCHAR(150) NOT NULL UNIQUE,
    domain_name VARCHAR(100) NOT NULL,
    funding_stage VARCHAR(50) NOT NULL,
    founding_date DATE NOT NULL,
    team_size INT NOT NULL CHECK (team_size >= 0),
    headquarters_city VARCHAR(100),
    website_url VARCHAR(255),
    description TEXT,
    incubator_status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    funding_status VARCHAR(50) NOT NULL DEFAULT 'BOOTSTRAPPED',
    funding_requirements TEXT,
    performance_score DECIMAL(5,2),
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at DATETIME NULL,
    target_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_raised DECIMAL(15,2) NOT NULL DEFAULT 0,
    equity_allocated DECIMAL(5,2) NOT NULL DEFAULT 0,
    investor_count INT NOT NULL DEFAULT 0,
    created_by INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE creates (
    startup_member_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT NOT NULL,
    user_id INT NOT NULL,
    member_role VARCHAR(50) NOT NULL,
    joined_on DATE NOT NULL DEFAULT CURRENT_DATE,
    left_on DATE,
    is_primary_contact BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (startup_id, user_id),
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE milestones (
    milestone_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT NOT NULL,
    milestone_title VARCHAR(150) NOT NULL,
    milestone_description TEXT,
    target_date DATE,
    completion_date DATE,
    milestone_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0 CHECK (progress_percent BETWEEN 0 AND 100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id)
);

CREATE TABLE investor_interests (
    interest_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT NOT NULL,
    investor_id INT NOT NULL,
    interest_status VARCHAR(30) NOT NULL DEFAULT 'INITIATED',
    pipeline_stage VARCHAR(50) NOT NULL DEFAULT 'INTRODUCTION',
    notes TEXT,
    responded_by INT NULL,
    response_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id),
    FOREIGN KEY (investor_id) REFERENCES users(user_id),
    FOREIGN KEY (responded_by) REFERENCES users(user_id)
);

CREATE TABLE funding_rounds (
    funding_round_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT NOT NULL,
    round_name VARCHAR(100) NOT NULL,
    round_type VARCHAR(50) NOT NULL,
    amount_raised DECIMAL(15,2) NOT NULL CHECK (amount_raised >= 0),
    equity_percentage DECIMAL(5,2) NOT NULL CHECK (equity_percentage BETWEEN 0 AND 100),
    lead_investor_id INT,
    mou_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    round_status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    announced_on DATE,
    closed_on DATE,
    created_by INT NOT NULL,
    investment_requirements TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id),
    FOREIGN KEY (lead_investor_id) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE funding_round_investors (
    funding_round_id INT NOT NULL,
    investor_id INT NOT NULL,
    contribution_amount DECIMAL(15,2) NOT NULL CHECK (contribution_amount >= 0),
    equity_held DECIMAL(5,2) NOT NULL CHECK (equity_held BETWEEN 0 AND 100),
    expected_return_multiple DECIMAL(8,2),
    PRIMARY KEY (funding_round_id, investor_id),
    FOREIGN KEY (funding_round_id) REFERENCES funding_rounds(funding_round_id),
    FOREIGN KEY (investor_id) REFERENCES users(user_id)
);

CREATE TABLE activity_logs (
    activity_log_id INT PRIMARY KEY AUTO_INCREMENT,
    actor_user_id INT NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    action_type VARCHAR(30) NOT NULL,
    action_summary VARCHAR(255) NOT NULL,
    old_values TEXT,
    new_values TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_user_id) REFERENCES users(user_id)
);

-- App extension tables used by the current web workflow.
CREATE TABLE investment_commitments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT NOT NULL,
    investor_id INT NOT NULL,
    interest_id INT NULL,
    requested_amount DECIMAL(15,2) NOT NULL,
    approved_amount DECIMAL(15,2) NULL,
    equity_percentage DECIMAL(5,2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    startup_requirements TEXT,
    investor_notes TEXT,
    decision_notes TEXT,
    decided_by INT NULL,
    agreed_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id),
    FOREIGN KEY (investor_id) REFERENCES users(user_id),
    FOREIGN KEY (interest_id) REFERENCES investor_interests(interest_id),
    FOREIGN KEY (decided_by) REFERENCES users(user_id)
);

CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    recipient_user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    link VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_startups_domain_stage ON startups(domain_name, funding_stage);
CREATE INDEX idx_startups_status ON startups(incubator_status, funding_status);
CREATE INDEX idx_milestones_startup_status ON milestones(startup_id, milestone_status);
CREATE INDEX idx_investor_interests_status ON investor_interests(investor_id, interest_status);
CREATE INDEX idx_funding_rounds_startup ON funding_rounds(startup_id, round_status);
CREATE INDEX idx_activity_logs_entity ON activity_logs(entity_type, entity_id, created_at);

INSERT INTO roles (role_name, description) VALUES
('ADMIN', 'System administrator with full incubator management access'),
('STARTUP_REP', 'Startup representative managing startup-side records'),
('INVESTOR', 'Investor reviewing startups and portfolio information');

INSERT INTO permissions (permission_code, description) VALUES
('USER_REGISTER', 'Register into the system'),
('USER_LOGIN', 'Login to the system'),
('STARTUP_CREATE', 'Create startup records'),
('STARTUP_UPDATE', 'Update startup records'),
('STARTUP_DELETE', 'Remove startup records'),
('STARTUP_VIEW', 'View startup records'),
('INTEREST_CREATE', 'Express investment interest'),
('FUNDING_MANAGE', 'Manage funding rounds'),
('AUDIT_VIEW', 'View audit trail'),
('PORTFOLIO_VIEW', 'View investor portfolio'),
('SEARCH_ALL', 'Search all entities');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON
    (r.role_name = 'ADMIN' AND p.permission_code IN (
        'USER_LOGIN', 'STARTUP_CREATE', 'STARTUP_UPDATE', 'STARTUP_DELETE',
        'STARTUP_VIEW', 'FUNDING_MANAGE',
        'AUDIT_VIEW', 'SEARCH_ALL'
    ))
    OR
    (r.role_name = 'STARTUP_REP' AND p.permission_code IN (
        'USER_REGISTER', 'USER_LOGIN', 'STARTUP_VIEW', 'SEARCH_ALL'
    ))
    OR
    (r.role_name = 'INVESTOR' AND p.permission_code IN (
        'USER_REGISTER', 'USER_LOGIN', 'STARTUP_VIEW', 'INTEREST_CREATE',
        'PORTFOLIO_VIEW', 'SEARCH_ALL'
    ));

CREATE VIEW investor_portfolio_summary AS
SELECT
    fri.investor_id,
    u.full_name AS investor_name,
    s.startup_id,
    s.startup_name,
    SUM(fri.contribution_amount) AS total_invested,
    SUM(fri.equity_held) AS total_equity_held,
    AVG(fri.expected_return_multiple) AS avg_expected_return_multiple
FROM funding_round_investors fri
JOIN users u ON u.user_id = fri.investor_id
JOIN funding_rounds fr ON fr.funding_round_id = fri.funding_round_id
JOIN startups s ON s.startup_id = fr.startup_id
GROUP BY fri.investor_id, u.full_name, s.startup_id, s.startup_name;
