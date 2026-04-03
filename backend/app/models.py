from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column("role_id", db.Integer, primary_key=True)
    name = db.Column("role_name", db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship("User", back_populates="role")


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column("user_id", db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    organization_name = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime)

    role = db.relationship("Role", back_populates="users")
    startup_memberships = db.relationship("StartupMember", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "fullName": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "organizationName": self.organization_name,
            "role": self.role.name,
        }


class Startup(TimestampMixin, db.Model):
    __tablename__ = "startups"

    id = db.Column("startup_id", db.Integer, primary_key=True)
    name = db.Column("startup_name", db.String(150), unique=True, nullable=False)
    domain = db.Column("domain_name", db.String(100), nullable=False)
    funding_stage = db.Column(db.String(50), nullable=False)
    founding_date = db.Column(db.Date, nullable=False)
    team_size = db.Column(db.Integer, nullable=False)
    headquarters_city = db.Column(db.String(100))
    website_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    incubator_status = db.Column(db.String(30), default="ACTIVE", nullable=False)
    funding_status = db.Column(db.String(50), default="BOOTSTRAPPED", nullable=False)
    funding_requirements = db.Column(db.Text)
    performance_score = db.Column(db.Float)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime)
    target_amount = db.Column(db.Float, default=0, nullable=False)
    total_raised = db.Column(db.Float, default=0, nullable=False)
    equity_allocated = db.Column(db.Float, default=0, nullable=False)
    investor_count = db.Column(db.Integer, default=0, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    milestones = db.relationship("Milestone", back_populates="startup", cascade="all, delete-orphan")
    members = db.relationship("StartupMember", back_populates="startup", cascade="all, delete-orphan")
    interests = db.relationship("InvestorInterest", back_populates="startup", cascade="all, delete-orphan")
    funding_rounds = db.relationship("FundingRound", back_populates="startup", cascade="all, delete-orphan")
    commitments = db.relationship("InvestmentCommitment", back_populates="startup", cascade="all, delete-orphan")

    def to_dict(self):
        accepting_investment = (
            self.is_published
            and self.incubator_status not in {"FUNDED", "CLOSED"}
            and (self.equity_allocated or 0) < 100
            and (not self.target_amount or (self.total_raised or 0) < self.target_amount)
        )
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "fundingStage": self.funding_stage,
            "foundingDate": self.founding_date.isoformat(),
            "teamSize": self.team_size,
            "headquartersCity": self.headquarters_city,
            "websiteUrl": self.website_url,
            "description": self.description,
            "incubatorStatus": self.incubator_status,
            "fundingStatus": self.funding_status,
            "fundingRequirements": self.funding_requirements,
            "performanceScore": self.performance_score,
            "isPublished": self.is_published,
            "publishedAt": self.published_at.isoformat() if self.published_at else None,
            "acceptingInvestment": accepting_investment,
            "targetAmount": self.target_amount,
            "totalRaised": self.total_raised,
            "equityAllocated": self.equity_allocated,
            "equityRemaining": max(0, 100 - (self.equity_allocated or 0)),
            "investorCount": self.investor_count,
            "milestones": [milestone.to_dict() for milestone in self.milestones],
            "fundingRounds": [funding_round.to_dict() for funding_round in self.funding_rounds],
            "members": [member.to_dict() for member in self.members],
            "interests": [interest.to_dict() for interest in self.interests],
            "commitments": [commitment.to_dict() for commitment in self.commitments],
        }


class StartupMember(TimestampMixin, db.Model):
    __tablename__ = "creates"

    id = db.Column("startup_member_id", db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.startup_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    member_role = db.Column(db.String(50), nullable=False)
    joined_on = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)
    left_on = db.Column(db.Date)
    is_primary_contact = db.Column(db.Boolean, default=False, nullable=False)

    startup = db.relationship("Startup", back_populates="members")
    user = db.relationship("User", back_populates="startup_memberships")

    def to_dict(self):
        return {
            "id": self.id,
            "startupId": self.startup_id,
            "userId": self.user_id,
            "memberRole": self.member_role,
            "isPrimaryContact": self.is_primary_contact,
            "fullName": self.user.full_name if self.user else None,
            "email": self.user.email if self.user else None,
        }


class Milestone(TimestampMixin, db.Model):
    __tablename__ = "milestones"

    id = db.Column("milestone_id", db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.startup_id"), nullable=False)
    title = db.Column("milestone_title", db.String(150), nullable=False)
    description = db.Column("milestone_description", db.Text)
    target_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    status = db.Column("milestone_status", db.String(30), default="PENDING", nullable=False)
    progress_percent = db.Column(db.Float, default=0, nullable=False)

    startup = db.relationship("Startup", back_populates="milestones")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "targetDate": self.target_date.isoformat() if self.target_date else None,
            "completionDate": self.completion_date.isoformat() if self.completion_date else None,
            "status": self.status,
            "progressPercent": self.progress_percent,
        }


class InvestorInterest(TimestampMixin, db.Model):
    __tablename__ = "investor_interests"

    id = db.Column("interest_id", db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.startup_id"), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    status = db.Column("interest_status", db.String(30), default="INITIATED", nullable=False)
    pipeline_stage = db.Column(db.String(50), default="INTRODUCTION", nullable=False)
    notes = db.Column(db.Text)
    responded_by = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    response_notes = db.Column(db.Text)

    startup = db.relationship("Startup", back_populates="interests")
    investor = db.relationship("User", foreign_keys=[investor_id])
    responder = db.relationship("User", foreign_keys=[responded_by])

    def to_dict(self):
        return {
            "id": self.id,
            "startupId": self.startup_id,
            "investorId": self.investor_id,
            "status": self.status,
            "pipelineStage": self.pipeline_stage,
            "notes": self.notes,
            "investorName": self.investor.full_name if self.investor else None,
            "responseNotes": self.response_notes,
            "respondedBy": self.responded_by,
            "createdAt": self.created_at.isoformat(),
        }


class FundingRound(TimestampMixin, db.Model):
    __tablename__ = "funding_rounds"

    id = db.Column("funding_round_id", db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.startup_id"), nullable=False)
    round_name = db.Column(db.String(100), nullable=False)
    round_type = db.Column(db.String(50), nullable=False)
    amount_raised = db.Column(db.Float, nullable=False)
    equity_percentage = db.Column(db.Float, nullable=False)
    mou_status = db.Column(db.String(30), default="PENDING", nullable=False)
    round_status = db.Column(db.String(30), default="OPEN", nullable=False)
    lead_investor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    announced_on = db.Column(db.Date)
    closed_on = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    investment_requirements = db.Column(db.Text)

    startup = db.relationship("Startup", back_populates="funding_rounds")
    lead_investor = db.relationship("User", foreign_keys=[lead_investor_id])

    def to_dict(self):
        return {
            "id": self.id,
            "startupId": self.startup_id,
            "roundName": self.round_name,
            "roundType": self.round_type,
            "amountRaised": self.amount_raised,
            "equityPercentage": self.equity_percentage,
            "mouStatus": self.mou_status,
            "roundStatus": self.round_status,
            "leadInvestorId": self.lead_investor_id,
            "leadInvestorName": self.lead_investor.full_name if self.lead_investor else None,
            "announcedOn": self.announced_on.isoformat() if self.announced_on else None,
            "closedOn": self.closed_on.isoformat() if self.closed_on else None,
            "createdBy": self.created_by,
            "createdAt": self.created_at.isoformat(),
            "investmentRequirements": self.investment_requirements,
        }


class InvestmentCommitment(TimestampMixin, db.Model):
    __tablename__ = "investment_commitments"

    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.startup_id"), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey("investor_interests.interest_id"))
    requested_amount = db.Column(db.Float, nullable=False)
    approved_amount = db.Column(db.Float)
    equity_percentage = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="PENDING", nullable=False)
    startup_requirements = db.Column(db.Text)
    investor_notes = db.Column(db.Text)
    decision_notes = db.Column(db.Text)
    decided_by = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    agreed_at = db.Column(db.DateTime)

    startup = db.relationship("Startup", back_populates="commitments")
    investor = db.relationship("User", foreign_keys=[investor_id])
    interest = db.relationship("InvestorInterest")
    decider = db.relationship("User", foreign_keys=[decided_by])

    def to_dict(self):
        return {
            "id": self.id,
            "startupId": self.startup_id,
            "investorId": self.investor_id,
            "interestId": self.interest_id,
            "requestedAmount": self.requested_amount,
            "approvedAmount": self.approved_amount,
            "equityPercentage": self.equity_percentage,
            "status": self.status,
            "startupRequirements": self.startup_requirements,
            "investorNotes": self.investor_notes,
            "decisionNotes": self.decision_notes,
            "investorName": self.investor.full_name if self.investor else None,
            "decidedBy": self.decided_by,
            "agreedAt": self.agreed_at.isoformat() if self.agreed_at else None,
            "createdAt": self.created_at.isoformat(),
        }


class ActivityLog(TimestampMixin, db.Model):
    __tablename__ = "activity_logs"

    id = db.Column("activity_log_id", db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action_type = db.Column(db.String(30), nullable=False)
    action_summary = db.Column(db.String(255), nullable=False)
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)

    actor = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "actor": self.actor.full_name if self.actor else None,
            "entityType": self.entity_type,
            "entityId": self.entity_id,
            "actionType": self.action_type,
            "actionSummary": self.action_summary,
            "createdAt": self.created_at.isoformat(),
        }


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(255))

    recipient = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "recipientUserId": self.recipient_user_id,
            "title": self.title,
            "message": self.message,
            "isRead": self.is_read,
            "link": self.link,
            "createdAt": self.created_at.isoformat(),
        }
