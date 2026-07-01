"""Vérification du numéro Ordre Infirmiers (CDC F1.3).

Mock en développement : l'intégration réelle avec l'API publique de l'Ordre
se substituera à cette implémentation sans changer sa signature.
"""

ORDER_NUMBER_LENGTH = 6


def verify_order_number(order_number: int) -> bool:
    """Retourne True si le numéro Ordre est considéré comme valide (mock)."""
    return len(str(order_number)) >= ORDER_NUMBER_LENGTH
