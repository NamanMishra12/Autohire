from enum import Enum


class ResumeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ParsingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    INTERVIEW = "INTERVIEW"


class JobSource(str, Enum):
    LINKEDIN = "LINKEDIN"
    INDEED = "INDEED"
    NAUKRI = "NAUKRI"
    GREENHOUSE = "GREENHOUSE"
    LEVER = "LEVER"