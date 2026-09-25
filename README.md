# INFIRMO — Backend (T-ESP-800)

[![CI](https://github.com/Yohan-Baechle/T-ESP-800-BACKEND/actions/workflows/ci.yml/badge.svg)](https://github.com/Yohan-Baechle/T-ESP-800-BACKEND/actions/workflows/ci.yml)

API backend du projet **INFIRMO**, le réseau professionnel des infirmiers
libéraux (mise en relation pour remplacements et collaborations entre cabinets
titulaires et remplaçants). Projet Epitech Nancy (MSC 2027).

> Projet en cours de développement. La structure des routers suit le cahier des
> charges ; les endpoints sont ajoutés au fur et à mesure de leur implémentation.

## Périmètre fonctionnel (CDC)

Le backend est organisé par domaine métier, un router par périmètre :

| Router            | Responsabilité                                            |
|-------------------|-----------------------------------------------------------|
| `users`           | Comptes, authentification, rôles cabinet / remplaçant     |
| `profils`         | Profils professionnels                                    |
| `documents`       | Gestion des documents                                     |
| `recherche`       | Recherche et mise en relation                             |
| `remplacements`   | Annonces et gestion des remplacements                     |
| `communication`   | Messagerie / notifications                                |
| `internal/admin`  | Administration                                            |

## Stack technique

- **Python** / **FastAPI**
- **Pydantic v2** (validation & settings)
- **Uvicorn** (serveur ASGI)
- `email-validator`, `python-multipart`, `python-dotenv`

## Mise en route

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Documentation interactive auto-générée : http://localhost:8000/docs

## Structure

```
app/
├── main.py            Point d'entrée FastAPI
├── dependencies.py    Dépendances partagées
├── routers/           Un module par périmètre métier
└── internal/          Endpoints d'administration
```

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
