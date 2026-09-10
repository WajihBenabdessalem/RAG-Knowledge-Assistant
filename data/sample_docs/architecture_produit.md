# Architecture technique — Plateforme Nova

## Vue d'ensemble

La plateforme Nova repose sur une architecture micro-services déployée sur
Kubernetes. Chaque service expose une API REST documentée en OpenAPI et
communique via un bus d'événements (Kafka) pour les flux asynchrones.

## Composants principaux

- **nova-gateway** : point d'entrée unique (API Gateway), authentification et
  routage vers les services internes.
- **nova-core** : logique métier principale, base de données PostgreSQL dédiée.
- **nova-analytics** : agrégation des événements et calcul des indicateurs,
  base de données ClickHouse.

## Déploiement et CI/CD

Chaque service dispose de son propre pipeline GitHub Actions : lint, tests
unitaires, build de l'image Docker, puis déploiement automatique en
environnement de staging après merge sur `main`. Le déploiement en production
nécessite une validation manuelle (approbation d'un lead technique).

## Observabilité

Les logs sont centralisés via Loki, les métriques via Prometheus/Grafana, et
le tracing distribué via OpenTelemetry. Toute alerte critique déclenche une
notification PagerDuty vers l'équipe d'astreinte.
