# Sources et ressources utilisées pour StuGo CO2 Explorer

Liste des documentations et références techniques utilisées pendant le développement, avec pour chacune ce qu'elle a concrètement apporté au projet.

---

## 1. PyQt6 — documentation officielle *(anglais)*
https://www.riverbankcomputing.com/static/Docs/PyQt6/

Base de toute l'interface graphique : `QMainWindow`, `QWidget`, signaux/slots, `QAbstractTableModel` (tableau de données), `QScrollArea` / `QSizePolicy` (barre de filtres et pages responsives).

## 2. Qt 6 — Reference *(anglais)*
https://doc.qt.io/qt-6/

Référence des classes Qt sous-jacentes à PyQt6 : `QAbstractTableModel` et `QSortFilterProxyModel` (utilisés dans l'outil Admin_Logs), propriétés de layout (`QHBoxLayout`, `QVBoxLayout`, `QGridLayout`).

## 3. pandas — User Guide & API reference *(anglais)*
https://pandas.pydata.org/docs/

Chargement des fichiers Excel/CSV, agrégations `groupby` par zone d'émission et par faculté, filtrage des `DataFrame` dans `FilterSidebar.apply()` et `DataService`.

## 4. NumPy — documentation *(anglais)*
https://numpy.org/doc/stable/

Calculs vectoriels utilisés dans la géométrie des graphiques 3D (`rendering/geometry/cube_3d.py`, `pie_3d.py`) : coordonnées des faces de cubes et des parts de camembert en volume.

## 5. Matplotlib — documentation et galerie mplot3d *(anglais)*
https://matplotlib.org/stable/

Tous les graphiques 2D/3D de l'application. La documentation de `Poly3DCollection` et de son paramètre de tri `zsort` a été déterminante pour diagnostiquer et corriger le bug de chevauchement des formes 3D : dessiner chaque cube/part comme sa **propre** collection plutôt que de regrouper toutes les faces ensemble.

## 6. python-docx — documentation *(anglais)*
https://python-docx.readthedocs.io/

Génération automatisée des rapports de sprint, de tests, techniques et du rapport complet (scripts `make_*.py`).

## 7. PyInstaller — documentation *(anglais)*
https://pyinstaller.org/en/stable/

Empaquetage de l'application en exécutable Windows autonome (mode *frozen*, détection du dossier `_internal`, gestion des chemins `%LOCALAPPDATA%`).

## 8. docs.python.org/fr/3/ — documentation officielle Python *(français)*
https://docs.python.org/fr/3/

Traduction officielle de la référence du langage : `dataclasses` (figées) pour `ChartConfig`, `typing.Protocol` pour les interfaces de dépôt (`ISessionRepository`), `threading.Lock` pour `FileLogger`.

## 9. refactoring.guru — Design Patterns *(français)*
https://refactoring.guru/fr/design-patterns

Identification et vocabulaire des patrons de conception réellement présents dans l'architecture : Singleton (services), Repository, Factory, Strategy (moteurs de rendu 2D/3D), Command (historique d'annulation), Observer (`EventBus`), Médiateur (`MainWindow`).

## 10. Developpez.com — communauté de développeurs francophone *(français)*
https://www.developpez.com

Communauté francophone de référence pour des tutoriels PyQt/pandas en français, utile pour vérifier des usages spécifiques de widgets Qt en contexte francophone.

---

*Cette liste couvre les sources générales consultées pendant le développement ; elle ne remplace pas la documentation technique du projet (voir `README.md` et `Rapport_Complet_StuGoCO2.docx`).*
