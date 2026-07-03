# INFIRMO — Backend

API du réseau professionnel des infirmiers libéraux (projet Epitech **T-ESP-800**).

Ce dépôt est le **service backend** du projet INFIRMO : il expose une API REST
sécurisée pour la mise en relation des infirmiers libéraux (remplacements,
recherche géolocalisée, messagerie, transmissions patient).

## Stack technique

| Couche | Technologie |
| --- | --- |
| Langage | Python 3.12 |
| Framework API | FastAPI |
| Base de données | PostgreSQL + PostGIS (géospatial) |
| ORM / migrations | SQLAlchemy 2.0 / Alembic |
| Authentification | JWT (python-jose), mots de passe bcrypt |
| Chiffrement au repos | AES-256-GCM (données de santé) |
| Conteneurisation | Docker / Docker Compose |
| Qualité | pytest, Ruff, Black, Bandit |

## Démarrage rapide (Docker)

Prérequis : Docker et Docker Compose.

```bash
cp .env.example .env          # puis renseigner les secrets
docker compose up --build     # db (PostGIS), redis, api
```

L'API est disponible sur http://localhost:8000 :

- Documentation Swagger : http://localhost:8000/docs
- Documentation ReDoc : http://localhost:8000/redoc

## Démarrage local (sans Docker pour l'API)

Nécessite une base PostgreSQL avec PostGIS accessible (via
`docker compose up -d db redis`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
alembic upgrade head          # applique les migrations
fastapi dev app/main.py       # serveur de développement
```

## Structure du projet

```
app/
├── main.py            # application FastAPI, montage des routers
├── core/              # config, base de données, sécurité, chiffrement
├── models/            # modèles SQLAlchemy (schéma Merise)
├── schemas/           # schémas Pydantic (entrées/sorties)
├── routers/           # endpoints par domaine métier
├── services/          # logique transverse (audit, vérifications)
├── middleware/        # middleware HTTP (audit)
├── dependencies.py    # dépendances partagées (session DB)
└── internal/          # endpoints d'administration
alembic/               # migrations de base de données
tests/                 # tests pytest (base de test isolée)
```

## Domaines fonctionnels

| Préfixe | Domaine |
| --- | --- |
| `/api/v1/auth` | Inscription, connexion (JWT), profil courant |
| `/api/v1/profiles` | Consultation et mise à jour du profil infirmier |
| `/api/v1/documents` | Documents légaux (upload PDF, vérification Ordre) |
| `/api/v1/nursing-offices` | Cabinets et leur localisation |
| `/api/v1/offers` | Publication et recherche d'offres de remplacement |
| `/api/v1/cares` | Référentiel des types de soins |
| `/api/v1/conversations` | Messagerie sécurisée entre professionnels |
| `/api/v1/patients` | Dossiers patients et transmissions sécurisées |
| `/api/v1/me` | Activité de l'utilisateur (candidatures, offres) |
| `/api/v1/admin` | Journal d'audit, purge RGPD |
| `/health`, `/health/ready` | Sondes de disponibilité (liveness / readiness) |

### Pagination

Les listes volumineuses (offres, candidatures, messages, patients,
transmissions, journal d'audit) sont paginées via les paramètres `limit`
(1–100, défaut 20) et `offset`. La réponse est enveloppée :

```json
{ "items": [...], "total": 42, "limit": 20, "offset": 0 }
```

## Sécurité et conformité

- **Authentification** JWT, mots de passe hachés (bcrypt).
- **Chiffrement au repos** AES-256-GCM des données de santé sensibles.
- **RGPD** : conservation limitée des transmissions (30 jours), droit à
  l'oubli (anonymisation des dossiers patients).
- **Audit** : traçabilité des accès (middleware) et des actions sensibles.

## Tests et qualité

```bash
pytest                        # tests (base PostgreSQL de test dédiée)
ruff check .                  # linting
black --check app tests       # formatage
bandit -r app -c pyproject.toml   # analyse de sécurité
```

Ces contrôles sont exécutés automatiquement en intégration continue
(GitHub Actions) à chaque push sur `main` et `develop`.

## Conventions Git

- **Branches** : `feature/<desc>`, `bugfix/<desc>`, `docs/<desc>`,
  `refactor/<desc>`, `test/<desc>`, `ci/<desc>`.
- **Flux** : `feature/*` → `develop` (squash merge) → `main`.
- **Commits** : convention [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`).
