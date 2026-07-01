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
