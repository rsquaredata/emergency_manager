<div align="center">

# Emergency Manager

### *Gestion logistique agentique des urgences hospitalières*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-Système%20agentique-purple.svg)]()
[![Santé](https://img.shields.io/badge/Application-Urgences%20hospitalières-red.svg)]()
[![License](https://img.shields.io/badge/License-Académique-lightgrey.svg)]()

*Projet de Master 2 SISE - Data for Good*
*Université Lumière Lyon 2 | 2025-2026*

[Aperçu](#aperçu) • [Objectifs](#objectifs) • [Architecture du système](#architecture-du-système) • [Machine Learning](#machine-learning) • [LLM--RAG](#llm--rag) • [Simulation & Interface](#simulation--interface)

---

</div>

## Table des matières

* [Aperçu](#aperçu)
* [Objectifs](#objectifs)
* [Points clés du projet](#points-clés-du-projet)
* [Architecture du système](#architecture-du-système)
* [Machine Learning](#machine-learning)
* [LLM & RAG](#llm--rag)
* [Simulation & Interface](#simulation--interface)
* [Métriques & Supervision](#métriques--supervision)
* [Structure du projet](#structure-du-projet)
* [Reproductibilité](#reproductibilité)
* [Limites](#limites)
* [Licence](#licence)

---

## Aperçu

**Emergency Mnager** est un projet académique consacré à la **gestion logistique des flux de patients dans un service d'urgences hospitalières**, à l'aide d'une **architecture agentique**, de **méthodes de machine learning** et de **modèles de langage (LLM)**.

Les services d'urgences sont soumis à de fortes contraintes : ressources médicales limitées, arrivées imprévisibles de patients, niveaux de gravité hétérogènes et pression temporelle constante.  
L'objectif de ce projet est de concevoir un **assistant d'aide à la décision** capable de :

- suivre l'état global du service d'urgences,
- gérer les flux de patients et l'allocation des ressources,
- expliquer les décisions du système en langage naturel à destination du personnel médical.

Le système est conçu comme un **outil de support**, et non comme un substitut au jugement médical humain.

---

## Objectifs

Le projet s'articule autour de trois objectifs complémentaires :

### 1. Gestion logistique et des flux

- Suivi des patients tout au long de leur parcours aux urgences
- Allocation de ressources limitées (salles, personnel, unités hospitalières)
- Détection des engorgements et goulets d'étranglement en temps réel

### 2. Aide à la décision et explicabilité

- Explication des décisions et priorisations du système
- Interaction avec le système via le langage naturel
- Transparence et traçabilité des recommandations

### 3. IA responsable et sobre

- Utilisation de modèles légers lorsque possible
- Contrôle de la latence, des coûts et de l'impact environnemental
- Justification explicite des choix architecturaux et algorithmiques

---

## Points clés du projet

- Modélisation agentique d'un service d'urgences
- Séparation explicite entre :
  - logique métier (sans IA),
  - machine learning,
  - raisonnement et explication via LLM
- Trois briques de machine learning complémentaires :
  - prédiction du temps d'attente,
  - clustering de situations de surcharge,
  - classification du risque de blocage
- Pipeline de **Retrieval-Augmented Generation (RAG)** fondé sur des règles médicales et organisationnelles
- Interface interactive de simulation et de supervision
- Accent fort mis sur l'explicabilité et la sobriété des modèles

---

## Architecture du système

Le système repose sur un **agent logistique central** chargé d'orchestrer l'ensemble des décisions :

- **Agent Logistique** - coordination globale et arbitrage
- **Agent de Triage** - priorisation selon la gravité
- **Agent de Supervision** - détection des états anormaux et saturations

Les patients, ressources et contraintes sont modélisés explicitement à l'aide d'une représentation à états.

Une description détaillée du **modèle du système sans IA** est fournie dans le document suivant :

```
docs/system_model.md
```

---

## Machine Learning

Le projet intègre **trois briques de machine learning**, chacune répondant à un besoin opérationnel distinct :

### 1. Prédiction du temps d'attente (régression)

Estimation du temps d'attente des patients à partir :

- de la charge actuelle du service,
- des niveaux de gravité,
- des ressources disponibles.

### 2. Clustering des situations de surcharge

Identification de motifs récurrents d'engorgement afin de :

- caractériser les états de stress du service,
- anticiper les situations critiques.

### 3. Classification du risque de blocage

Prédiction du risque qu'un patient bloque des ressources aval (unités hospitalières, soins critiques, etc.).

Une version **baseline sans machine learning** (entièrement fondée sur des règles) est fournie à des fins de comparaison.

---

## LLM & RAG

Les modèles de langage sont utilisés **uniquement pour le raisonnement et l'explication**, et jamais pour la prise de décision directe.

Le système intègre :

* un client LLM léger,
* un pipeline de **Retrieval-Augmented Generation (RAG)** bâti sur :

  - les règles des urgences,
  - les catégories de gravité,
  - les contraintes organisationnelles.

Exemples de requêtes utilisateur :

- *Pourquoi ce patient est-il encore en attente ?*
- *Que se passe-t-il si trois patients critiques arrivent maintenant ?*
- *Quelle unité est actuellement saturée, et pour quelle raison ?*

---

## Simulation & Interface

Une interface web interactive permet de :

- ajouter des patients avec une gravité et une localisation paramétrables,
- observer l'évolution en temps réel de l'état du service,
- interagir avec le système via une interface de chat,
- rejouer des scénarios de simulation prédéfinis.

L'application est déployée en ligne et accessible sans installation locale.

---

## Métriques & Supervision

Le système expose des métriques **métier** et **système** :

### Métriques métier

- temps d'attente moyen par niveau de gravité,
- taux d'utilisation des ressources,
- durée et fréquence des congestions.

### Métriques système

- latence des appels LLM,
- nombre d'appels,
- estimation des coûts,
- indicateurs d'impact environnemental (proxies).

---

## Structure du projet

```
emergency_manager/
│
├── app/            # Interface web
├── agents/         # Logique agentique
├── core/           # Modèle du système (sans IA)
├── ml/             # Modules de machine learning
├── rag/            # Pipeline RAG
├── llm/            # Client LLM et prompts
├── simulation/     # Scénarios et générateurs
├── metrics/        # Supervision et tableaux de bord
├── docs/           # Architecture et méthodologie
└── tests/          # Tests unitaires
```

---

## Reproductibilité

Le projet est entièrement reproductible.

Les simulations, modèles et expériences peuvent être exécutés localement ou via l'interface hébergée.
Les configurations et graines aléatoires sont fixées afin d'assurer la cohérence des résultats.

---

## Limites

Ce projet constitue un **prototype conceptuel et pédagogique** :

- Il pose pas de diagnostic médical,
- Il ne remplace pas les professionnels de santé,
- Il ne revendique aucune validité clinique.

Tous les résultats sont destinés à l'**aide à la décision et à l'expérimentation**.

---

## Licence

Projet développé dans un cadre académique. Usage éducatif et de recherche uniquement.

---

<div align="center">

**Emergency Manager - Gestion logistique agentique des urgences hospitalières**

</div>
