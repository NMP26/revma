# REVMA V2 — infrastructure de développement

Socle de développement conteneurisé : React + TypeScript + Vite, FastAPI et SQLite. Cette étape ne migre aucun calcul de révision et ne modifie pas l'archive privée V6.9.33.

## Prérequis

- Docker Desktop récent avec le moteur Linux et Docker Compose v2 sous Windows 11 ; ou Docker Engine + le plugin Compose sous Linux.
- Git facultatif pour cloner le dépôt.
- Aucun Node.js, Python ni dépendance applicative n'est requis sur l'hôte.

## Démarrage sous Windows 11

1. Ouvrir Docker Desktop et attendre que le moteur soit démarré.
2. Dans PowerShell, se placer à la racine du dépôt.
3. Copier `.env.example` vers `.env` (facultatif : les valeurs par défaut conviennent) : `Copy-Item .env.example .env`.
4. Vérifier puis construire/démarrer les services :

	```powershell
	docker compose config
	docker compose up --build -d
	docker compose ps
	```

5. Ouvrir `http://localhost:5173`. L'API est disponible à `http://localhost:8000/api/health`.

## Démarrage sous Linux

À la racine du dépôt, après installation et démarrage de Docker Engine et du plugin Compose :

```sh
cp .env.example .env
docker compose config
docker compose up --build -d
docker compose ps
```

Ouvrir `http://localhost:5173` et vérifier `http://localhost:8000/api/health`.

`localhost` dans ces URLs est l'adresse d'accès depuis le navigateur sur la machine hôte. Entre conteneurs, Compose fournit le nom DNS `backend` ; le proxy Vite transmet `/api` à ce service. Le code React appelle les chemins relatifs `/api/...` et ne dépend pas d'une adresse d'hôte codée en dur.

## Développement

Les sources `frontend/` et `backend/` sont montées dans les conteneurs : Vite et Uvicorn rechargent les modifications automatiquement. Les dépendances Node résident dans un volume nommé distinct pour éviter qu'un montage Windows ne les masque. Le lockfile `frontend/package-lock.json` fixe les dépendances transitives ; `npm ci` le vérifie et installe exactement ces versions dans le conteneur au démarrage.

### TypeScript dans VS Code

Pour que l'analyse TypeScript de VS Code puisse résoudre `@types/node` sans installer Node.js ou les paquets sur Windows, ouvrir le dépôt dans le conteneur : installer l'extension Microsoft **Dev Containers**, puis lancer **Dev Containers: Reopen in Container** depuis la palette de commandes. La configuration `.devcontainer/` monte le dépôt et le volume Docker `frontend_node_modules` dans le conteneur, et sélectionne le TypeScript du projet. Les dépendances restent donc exclusivement dans Docker. Dans cette fenêtre distante, sélectionner **Use Workspace Version** si VS Code le demande.

- Frontend : `http://localhost:5173`
- Vérification API : `http://localhost:8000/api/health`
- SQLite : `data/revma.sqlite3` sur l'hôte, monté dans le backend sur `/data/revma.sqlite3`.
- Logs : `docker compose logs -f frontend backend`
- Arrêt sans supprimer les données : `docker compose down`

Les versions Python, Node, FastAPI, Uvicorn, React, TypeScript et Vite sont fixées dans les Dockerfiles et manifestes ; `frontend/package-lock.json` verrouille également les versions transitives npm. Lors d'un changement de dépendance frontend, exécuter `docker compose run --rm frontend npm install --save-exact <paquet>` pour mettre à jour le manifeste et le lockfile depuis le conteneur, puis reconstruire.

## Sauvegarde et restauration SQLite

À exécuter depuis la racine du dépôt avec les conteneurs disponibles. La sauvegarde inclut les WAL SQLite ; utiliser l'API `.backup` de SQLite plutôt qu'une simple copie du fichier pendant que l'application écrit.

### Sauvegarde

PowerShell :

```powershell
New-Item -ItemType Directory -Force backups | Out-Null
docker compose exec -T backend python -c "import os, sqlite3; src=sqlite3.connect(os.environ.get('DATABASE_PATH', '/data/revma.sqlite3')); dst=sqlite3.connect('/data/revma-backup.sqlite3'); src.backup(dst); dst.close(); src.close()"
docker compose cp backend:/data/revma-backup.sqlite3 ./backups/revma-$(Get-Date -Format yyyyMMdd-HHmmss).sqlite3
docker compose exec -T backend rm -f /data/revma-backup.sqlite3
```

Linux shell :

```sh
mkdir -p backups
docker compose exec -T backend python -c "import os, sqlite3; src=sqlite3.connect(os.environ.get('DATABASE_PATH', '/data/revma.sqlite3')); dst=sqlite3.connect('/data/revma-backup.sqlite3'); src.backup(dst); dst.close(); src.close()"
docker compose cp backend:/data/revma-backup.sqlite3 "./backups/revma-$(date +%Y%m%d-%H%M%S).sqlite3"
docker compose exec -T backend rm -f /data/revma-backup.sqlite3
```

Stocker les sauvegardes hors du dépôt (le dossier `backups/` est ignoré par Git) et vérifier régulièrement leur intégrité avec `sqlite3 <fichier> 'PRAGMA integrity_check;'` dans un environnement contenant SQLite.

### Restauration

Arrêter les services pour éviter les écritures concurrentes, puis remplacer le fichier de base par une sauvegarde vérifiée :

```sh
docker compose stop frontend backend
```

Copier le fichier choisi en `data/revma.sqlite3` (PowerShell : `Copy-Item -Force .\backups\<sauvegarde>.sqlite3 .\data\revma.sqlite3`; Linux : `cp ./backups/<sauvegarde>.sqlite3 ./data/revma.sqlite3`), puis redémarrer :

```sh
docker compose up -d
```

Toujours effectuer une sauvegarde avant une migration future et tester la restauration sur une copie de données.

## Données privées et sécurité

- `.env`, `data/`, `backups/` et `reference-privee/` sont exclus de Git. Ne pas y placer ou publier secrets/données réelles.
- Ne jamais ajouter ni modifier `reference-privee/Marche_Reviser_V6_9_33.html` dans le cadre de ce socle.
- Les ports hôte peuvent être changés dans `.env` si nécessaire.

## Services et santé

Compose démarre le frontend après que le backend ait passé son contrôle de santé. Les deux services disposent de sondes de santé et d'une politique `unless-stopped`. L'endpoint `/api/health` retourne un statut JSON, et le backend initialise la base SQLite persistante au démarrage.
