import enum


class UserStatus(enum.StrEnum):
    """Statut d'un compte utilisateur (CDC F1.1 / F1.3).

    - PENDING : inscrit, en attente de validation Ordre Infirmiers.
    - ACTIVE : compte vérifié et actif.
    - SUSPENDED : compte suspendu (modération / conformité).
    - DELETED : droit à l'oubli RGPD (CDC F6.4).
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class DocumentType(enum.StrEnum):
    """Type de document légal exigé à l'inscription (CDC F1.2)."""

    PROFESSIONAL_CARD = "professional_card"
    RIB = "rib"
    INSURANCE = "insurance"


class DocumentStatus(enum.StrEnum):
    """État de vérification d'un document légal (CDC F1.2 / F1.3)."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NursingOfficeStatus(enum.StrEnum):
    """Statut d'un cabinet infirmier (CDC F1.6)."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class OfferStatus(enum.StrEnum):
    """Statut d'une offre de remplacement (CDC F3.1 / F3.4).

    - OPEN : offre publiée, ouverte aux candidatures.
    - CLOSED : offre pourvue ou retirée.
    - EXPIRED : offre dont la date de validité est dépassée.
    """

    OPEN = "open"
    CLOSED = "closed"
    EXPIRED = "expired"


class ApplicationStatus(enum.StrEnum):
    """État d'une candidature à une offre (CDC F3.3).

    - SUBMITTED : candidature déposée, en attente de traitement.
    - REVIEWED : candidature traitée par le cabinet (voir décision).
    """

    SUBMITTED = "submitted"
    REVIEWED = "reviewed"


class ApplicationDecision(enum.StrEnum):
    """Décision du cabinet sur une candidature (CDC F3.3 / US-04)."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
