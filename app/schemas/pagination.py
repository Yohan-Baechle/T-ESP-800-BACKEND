from pydantic import BaseModel


class Page[T](BaseModel):
    """Enveloppe de réponse paginée.

    - ``items`` : éléments de la page courante.
    - ``total`` : nombre total d'éléments correspondant à la requête.
    - ``limit`` / ``offset`` : paramètres de pagination appliqués.
    """

    items: list[T]
    total: int
    limit: int
    offset: int
