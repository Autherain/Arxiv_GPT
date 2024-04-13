# PROJET FIL ROUGE

## Paramétrer le prototype
Chaque service applicatif possède son propre fichier de configuration présent dans `pfr/config` sous forme de fichiers `env.*`. Chacun de ces fichiers surcharge le fichier `.env.default`.

Si vous utilisez le prototype en mode docker, les services utiliseront les fichiers `.env.*.docker`

### Insérer sa clé API ChatGPT
Pour que l'Updater et l'Asker fonctionne, vous devez mentionner votre clé personnelle d'API dans leurs fichiers de configuration respectifs, au paramètres `CHATPGPT_VECTOR_GRAPHDB_OPENAI_API_KEY`, `LANGCHAIN_OPENAI_API_KEY` & `CHAT_GPT_KEY` dans les fichiers `pfr/config/env.asker.docker` et `pfr/config/env.updater.docker`

## Lancement de l'environnement docker

```sh
$ cd docker/
$ docker compose up
```

## Poser des questions ! 
Tester cette application via la documentation de l'API `http://localhost:8000/docs`

## Visualiser la base REDIS

Rendez vous à l'URL `http://localhost:8001/` lorsque l'environnement docker est lancé.
L'utilisateur de la base Redis est `pfr`, Le mot de passe `pfr_pwd`.

## Visualiser la base GRAPHDB

Rendez vous à l'URL `http://localhost:7200/` lorsque l'environnement docker est lancé.
L'administrateur est `admin`, Le mot de passe `root`.

## Visualiser la base NEO4J

Rendez vous à l'URL `http://localhost:7474/` lorsque l'environnement docker est lancé.
Il n'y a pas d'identifiants à renseigner.
## Fonctionnement d'un application

L'application est lancée via le script start_app.sh suivi du nom de l'application.
Les options sont `api`, `retriever`, `updater`, `asker`

:bulb: *Exemple*
```sh
$ cd pfr/
$ ./start_app.sh retriever
```

Le script shell va alors initier le script python correspondant `app_<nom de l'application>.py`.
Le script applicatif va initialiser ses composants via un script `boot.py` placé dans son sous dossier.
Cette séquence de boot va créer les services utile à son fonctionnement dans un ordre prédéfini.
Par la suite, le script applicatif va dérouler sa logique applicative.

:bulb: *Exemple*
```
- Récupérer la configuration applicative
- Initialiser le logger
- Créer le service de connection à la BDD
- etc
```

## Services applicatifs

### Receiver 
Le Receiver est le service permettant la récupération des articles depuis ARXiv. Il utilise pour cela les endpoints Open Archive Interface (OAI).
A partir de la réponse XML, il vérifie le contenu de la liste d'article reçue et transforme ces derniers en un ensemble de modèles applicatifs. Par la suite, il dépose chaque modèle d'article dans une queue Redis.
L'API ARXiV transmet un maximum de 1000 Article en une réponse. Si la totalité des éléments à recevoir est supérieure, un token permettant de continuer les interrogations de l'API est associé à la réponse. Le Receiver récupère cet élément et assure la continuation des requêtes tant que des articles sont à recevoir.
Un délai d'attente est paramétré entre deux interrogations successives afin de satisfaire aux limiteurs de flux mis en place par ARXiv.

### Updater
L'Updater permet de transformer les articles pour les déposer dans les bases graphes. Il écoute en permanence une queue Redis des modèles ingérés par le Receiver à transformer. L'updater sépare alors, pour chaque article, les éléments composants ce dernier. La donnée structurée est intégrée au graphe de connaissance stocké dans GraphDB. Le résumé de l'article est passé à ChatGPT qui va réaliser un embedding de ce dernier et retourner un vecteur permettant une future recherche en similarité. Le vecteur en question sera déposé dans Neo4J. 

### Asker
L'Asker est sert d'interface entre l'API ChatGPT et les bases Redis, GraphDB et Neo4j. Il construit une réponse à une question posée à partir des données. L'asker en écoute permanente sur la queue, récupère la question et le token. Il demande à GraphDB la structure du knowledge graph et fait générer à ChatGPT la requête SPARQL. Il effectue une recherche en similarité de l'abstract sur Neo4j. Il dépose finalement la réponse associée au token dans Redis.

### API
L'API Gateway et l'API servent d'interface entre l'utilisateur et Redis. L'utilisateur requête l'API Gateway qui transmet au service API. Le service API génère un token UUID qu'il associe à la question. Le token est retourné à l'utilisateur pour qu'il puisse venir récuperer sa réponse ultéreurement. Enfin, la question et son token associé sont déposés dans une queue Redis.

### Redis
:link:[Site Officiel](https://redis.io/)

Redis est une base de données open-source clé/valeur en mémoire, souvent utilisée comme magasin de données en cache, système de messagerie, et pour des applications de traitement en temps réel. 
Redis facilite la gestion des files d'attente pour les tâches à exécuter entre différents services (Receiver, Updater, API et Asker)

### GraphDB
:link:[Site Officiel](https://graphdb.ontotext.com/)

GraphDB est une base de données orientée graphe qui permet de stocker, gérer et interroger des données sous forme de graphes RDF. Elle offre un modèle de données flexible et puissant, adapté à la représentation de relations complexes entre les entités.

GraphDB permet de stocker le graphe de connaissance au format RDF natif, et de faire des interrogations SparQL native via la spécification [rdf4j](https://rdf4j.org/documentation/reference/rest-api/).

### Neo4J
:link:[Site Officiel](https://neo4j.com/fr/)

Neo4j est une base de données orientée graphe hautement performante et évolutive. Elle est conçue pour stocker, gérer et interroger des données sous forme de graphes.Neo4j permet de stocker les vectorisations des abstracts et rechercher en similarité native.

### Kong
:link:[Site Officiel](https://konghq.com/)

Kong joue un rôle crucial en tant qu'interface entre notre API et les utilisateurs. En acceptant les requêtes API et en les dirigeant vers les services appropriés, Kong simplifie l'interaction utilisateur et garantit une gestion efficace du trafic. De plus, les extensions et plugins disponibles dans Kong offrent un contrôle étendu sur les utilisateurs, permettant la mise en œuvre de politiques de sécurité avancées, la gestion des autorisations, et l'optimisation des performances des API, renforçant ainsi la fiabilité et la sécurité de notre architecture. 
