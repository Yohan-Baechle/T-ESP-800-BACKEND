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
