# StuGo CO2 Explorer — v6.1 Responsive

Application de bureau **PyQt6** pour visualiser et analyser les émissions CO2 liées à la mobilité étudiante. Elle charge des fichiers Excel structurés, calcule les totaux par zone d'émission, et propose de nombreux types de graphiques 2D/3D.

---

## Sommaire

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Lancement](#lancement)
- [Structure du projet](#structure-du-projet)
- [Architecture](#architecture)
- [Modules détaillés](#modules-détaillés)
- [Format des fichiers Excel attendus](#format-des-fichiers-excel-attendus)
- [Outil Admin — Analyseur de logs](#outil-admin--analyseur-de-logs)
- [Format des logs](#format-des-logs)
- [Thèmes et personnalisation](#thèmes-et-personnalisation)
- [Sessions et préférences](#sessions-et-préférences)
- [Patterns de conception utilisés](#patterns-de-conception-utilisés)
- [Notes pour les développeurs](#notes-pour-les-développeurs)

---

## Prérequis

| Composant | Version minimale |
|---|---|
| Python | 3.10+ |
| PyQt6 | 6.4+ |
| matplotlib | 3.7+ |
| pandas | 2.0+ |
| openpyxl | 3.1+ |
| squarify | 0.4+ (treemap) |

---

## Installation

```bash
git clone <url-du-repo>
cd stugoco2_v61_responsive
pip install PyQt6 matplotlib pandas openpyxl squarify
```

Aucun fichier de configuration n'est nécessaire au premier lancement. La session et les préférences sont créées automatiquement dans le dossier utilisateur.

---

## Lancement

```bash
# Application principale
python main.py

# Outil admin (analyseur de logs, standalone)
python admin.py
```

---

## Structure du projet

```
stugoco2_v61_responsive/
│
├── main.py                          # Point d'entrée de l'application
├── admin.py                         # Outil autonome d'analyse de logs
│
├── app/                             # Couche application (commandes, événements, services)
│   ├── bootstrap.py                 # Initialisation DPI + thème + stylesheet
│   ├── commands/
│   │   ├── base_command.py          # Pattern Command + historique undo
│   │   ├── apply_filter_command.py  # Commande de filtrage
│   │   └── load_files_command.py    # Commande de chargement avec undo
│   ├── events/
│   │   ├── event_bus.py             # Bus d'événements central (Observer)
│   │   └── app_events.py            # Constantes des types d'événements
│   └── services/
│       ├── data_service.py          # Façade orchestration des données
│       ├── chart_service.py         # Façade rendu graphique
│       └── export_service.py        # Export CSV/image
│
├── domain/                          # Couche domaine (règles métier)
│   ├── repositories/
│   │   └── i_session_repo.py        # Interface dépôt session
│   └── value_objects/
│       ├── chart_config.py          # Config graphique immuable (frozen dataclass)
│       └── color_value.py           # Objet-valeur couleur
│
├── infrastructure/                  # Couche infrastructure (I/O, persistance)
│   ├── extractors/
│   │   ├── excel_extractor.py       # Parsing + validation fichiers Excel
│   │   └── extractor_factory.py     # Factory d'extracteurs
│   ├── models/
│   │   └── pandas_model.py          # Adaptateur pandas → Qt MVC (QAbstractTableModel)
│   └── persistence/
│       ├── session_repository.py    # Persistance session JSON (Singleton)
│       ├── preferences_repository.py# Préférences utilisateur JSON
│       └── _compat_session_manager.py # API fonctionnelle rétrocompatible
│
├── presentation/                    # Couche présentation PyQt6
│   ├── main_window.py               # Fenêtre principale (Façade + Médiateur)
│   ├── splash_screen.py             # Écran de chargement
│   ├── mediator/
│   │   └── ui_mediator.py           # Médiateur de composants UI
│   ├── pages/
│   │   ├── base_page.py             # Page abstraite (Template Method)
│   │   ├── home/home_page.py        # Tableau de bord + statistiques
│   │   ├── import_/import_page.py   # Import de fichiers Excel
│   │   ├── table/table_page.py      # Tableau de données (MVC)
│   │   ├── chart/chart_page.py      # Graphique unique avec contrôles
│   │   ├── comparison/comparison_page.py  # Comparaison multi-fichiers
│   │   └── settings/settings_page.py      # Thème, préférences, session
│   ├── sidebar/
│   │   ├── nav_sidebar.py           # Navigation latérale (Composite)
│   │   ├── filter_sidebar.py        # Filtres dynamiques
│   │   └── log_panel.py             # Historique d'actions + session
│   ├── state/
│   │   ├── app_state.py             # État de l'application
│   │   └── states.py                # Définitions des états
│   ├── theme/
│   │   ├── stylesheet_builder.py    # Génération QSS (Builder)
│   │   ├── theme_manager.py         # Application des thèmes (Singleton)
│   │   └── preset_completer.py      # Auto-complétion des presets de thème
│   └── widgets/
│       ├── primitives.py            # Composants UI réutilisables
│       ├── chart_controls.py        # Barre d'outils graphique
│       └── factory/widget_factory.py # Factory de widgets
│
├── rendering/                       # Rendu graphique (matplotlib)
│   ├── factory.py                   # Factory de renderers
│   ├── interfaces/i_chart_renderer.py # Interface renderer
│   ├── strategies/
│   │   ├── renderer_2d.py           # Stratégies graphiques 2D
│   │   ├── renderer_3d.py           # Stratégies graphiques 3D
│   │   └── special_renderer.py      # Graphiques spéciaux (Mobilité vs CO2)
│   ├── axes/
│   │   ├── axes_2d.py               # Utilitaires axes 2D
│   │   └── axes_3d.py               # Utilitaires axes 3D
│   └── geometry/
│       ├── cube_3d.py               # Dessin cube 3D
│       └── pie_3d.py                # Dessin secteur 3D
│
├── shared/                          # Utilitaires transversaux
│   ├── constants.py                 # Toutes les constantes (palette, zones, pages)
│   ├── scaling.py                   # Classe S — mise à l'échelle DPI-aware
│   ├── color_utils.py               # Fonctions de manipulation de couleur
│   └── logging/
│       ├── action_logger.py         # Historique actions utilisateur (Singleton)
│       └── file_logger.py           # Logger fichier thread-safe
│
└── logs/                            # Fichiers de log générés à l'exécution
    └── log-AAAA-MM-JJ.txt
```

---

## Architecture

Le projet suit une **Clean Architecture** à 4 couches strictes, sans dépendance ascendante :

```
┌─────────────────────────────────────────┐
│         Presentation  (PyQt6)           │  pages, sidebar, widgets, thème
├─────────────────────────────────────────┤
│         Application   (Services)        │  commandes, événements, services
├─────────────────────────────────────────┤
│         Domain        (Métier)          │  value objects, interfaces repo
├─────────────────────────────────────────┤
│         Infrastructure (I/O)            │  Excel, JSON, pandas, persistance
└─────────────────────────────────────────┘
              shared/  (transversal)
              constants · scaling · logging
```

**Flux de démarrage :**

```
main.py
  → QApplication (style Fusion)
  → app/bootstrap.py
      → S.init(app)              # calcul DPI, toutes les tailles
      → ThemeManager.instance()
      → StylesheetBuilder.build() → QSS appliqué globalement
  → SplashScreen (450 ms)
  → presentation/main_window.py
      → pages (Home, Import, Table, Chart, Comparison, Settings)
      → sidebars (Nav, Filter, Log)
      → services (DataService, ChartService, ExportService)
```

---

## Modules détaillés

### `main.py`
Point d'entrée unique. Crée la `QApplication`, appelle `bootstrap`, affiche le splash screen puis ouvre la `MainWindow`. En cas d'erreur critique, affiche une `QMessageBox` et quitte proprement.

---

### `app/bootstrap.py`
Initialise l'environnement graphique dans l'ordre imposé par Qt :
1. `S.init(app)` — calcule toutes les dimensions selon le DPI de l'écran
2. `ThemeManager.instance()` — crée le singleton de thème
3. `QPalette` appliqué à l'application
4. Stylesheet QSS global appliqué via `StylesheetBuilder.build()`

---

### `shared/constants.py`
Source unique de vérité pour toutes les constantes de l'application :

- **`C`** — dictionnaire de couleurs de la palette *Arctic Ink* (thème sombre par défaut)
- **`ZONES`** — 5 zones d'émission CO2 avec labels, plages de colonnes et couleurs
- **`COLUMN_LABELS`** — noms d'affichage des colonnes DataFrame
- **`CHART_TYPES`** — liste des types de graphiques disponibles avec icônes
- **`PAGES`** — identifiants des pages de navigation

---

### `shared/scaling.py` — Classe `S`
Système DPI-aware critique. **Toutes** les tailles de l'interface passent par `S`.

```python
S.init(app)      # appeler une seule fois avant tout widget
S.font_base      # taille de police de base adaptée au DPI
S.btn_h          # hauteur standard des boutons
S.sp(16)         # 16 pixels logiques → pixels réels de l'écran
```

`S` est un module-singleton : valeurs calculées une fois, accédées directement.

---

### `app/events/event_bus.py` — `EventBus`
Bus d'événements central basé sur les signaux PyQt6. Découple totalement les composants.

```python
bus = EventBus.instance()
bus.subscribe("FILES_LOADED", mon_handler)
bus.publish("FILES_LOADED", payload={"count": 3})
bus.unsubscribe("FILES_LOADED", mon_handler)
```

Les types d'événements sont définis dans `app/events/app_events.py`.

---

### `app/commands/base_command.py` — `Command` + `CommandHistory`
Pattern Command avec support undo. Toute action réversible hérite de `Command`.

```python
class LoadFilesCommand(Command):
    def execute(self) -> bool: ...
    def undo(self) -> bool: ...
    def can_undo(self) -> bool: return True

history = CommandHistory(max_size=50)
history.execute(LoadFilesCommand(...))
history.undo_last()
```

---

### `app/services/data_service.py` — `DataService`
Façade singleton pour toutes les opérations sur les données. Coordonne l'extraction Excel, la mise à jour du modèle Qt, l'application des filtres et la publication d'événements vers les pages.

---

### `infrastructure/extractors/excel_extractor.py`
Lit et valide les fichiers Excel feuille par feuille. Vérifie la structure des colonnes, calcule les totaux CO2 par zone, et retourne des records normalisés. Les feuilles nommées `template` sont ignorées. Les doublons (même fichier + même feuille) sont écartés silencieusement.

---

### `infrastructure/models/pandas_model.py` — `PandasModel`
Adaptateur `pandas.DataFrame` → `QAbstractTableModel`. Permet d'afficher directement un DataFrame dans un `QTableView` PyQt6 avec tri, filtrage et sélection native.

---

### `infrastructure/persistence/`

| Fichier | Rôle |
|---|---|
| `session_repository.py` | Sauvegarde/restauration de la session (fichiers chargés, filtres actifs) en JSON |
| `preferences_repository.py` | Préférences utilisateur (thème, langue, colonnes) en JSON |
| `_compat_session_manager.py` | API fonctionnelle à utiliser dans tout le code |

**Utilisation recommandée dans le code :**

```python
from infrastructure.persistence import _compat_session_manager as session_manager

session = session_manager.load_session()
session_manager.save_session({"files": [...], "filters": {...}})
session_manager.clear_session()

prefs = session_manager.load_prefs()
session_manager.save_prefs({"theme": "Arctic Ink"})
```

---

### `domain/value_objects/chart_config.py` — `ChartConfig`
Frozen dataclass décrivant une configuration graphique complète. Immuable et hashable. Utiliser les méthodes `.with_*()` pour créer des variantes sans mutation.

```python
config = ChartConfig(chart_type="bar", y_col="total_tco2", top_n=10)
config_3d = config.with_3d(True)
```

---

### `presentation/main_window.py` — `MainWindow`
Fenêtre principale. Façade et Médiateur entre toutes les pages, sidebars et services. Les signaux UI sont connectés ici aux commandes et services applicatifs.

---

### `presentation/theme/stylesheet_builder.py` — `StylesheetBuilder`
Génère dynamiquement le QSS global à partir des couleurs de `C` et des tailles de `S`. Appelé automatiquement par `ThemeManager` lors d'un changement de thème.

---

### `rendering/`
Rendu graphique matplotlib. La sélection du renderer se fait via `rendering/factory.py` selon le type de graphique et le mode 2D/3D.

| Fichier | Contenu |
|---|---|
| `strategies/renderer_2d.py` | bar, barh, pie, donut, area, treemap, scatter |
| `strategies/renderer_3d.py` | bar3d, pie3d, cube3d |
| `strategies/special_renderer.py` | Graphiques métier (Mobilité vs CO2, répartition zones) |
| `geometry/cube_3d.py` | Dessin bas-niveau des cubes 3D |
| `geometry/pie_3d.py` | Dessin bas-niveau des secteurs 3D |
| `axes/axes_2d.py` | Style, labels, grille axes 2D |
| `axes/axes_3d.py` | Style, labels, rotation axes 3D |

---

## Format des fichiers Excel attendus

Chaque fichier `.xlsx` peut contenir **plusieurs feuilles** (une par faculté/département). Chaque feuille doit respecter cette structure de colonnes :

```
Colonnes 0–3   → Zone 1  (<0.5 tCO2e)  : pays | tco2e_par_voyage | nb_etudiants | ...
Colonnes 4–7   → Zone 2  (0.5–1 tCO2e)
Colonnes 8–11  → Zone 3  (1–2 tCO2e)
Colonnes 12–15 → Zone 4  (2–3 tCO2e)
Colonnes 16–19 → Zone 5  (>3 tCO2e)
```

- Les feuilles nommées `template` sont ignorées automatiquement.
- Une feuille sans données valides (pays ou tco2e absents) est signalée comme erreur dans les logs.
- Les doublons (même fichier + même feuille déjà chargé) sont ignorés sans notification.

---

## Outil Admin — Analyseur de logs

`admin.py` est un **outil autonome** indépendant de l'application principale. Il sert à lire, filtrer et analyser les fichiers de log générés par StuGo CO2 Explorer.

```bash
python admin.py
```

**Fonctionnalités :**

| Fonctionnalité | Description |
|---|---|
| Chargement dossier | Lit tous les fichiers `log-AAAA-MM-JJ.txt` d'un dossier |
| Tableau filtrable | Affiche date, heure, module, message avec tri par colonne |
| Recherche temps réel | Filtre par mot-clé dans tous les champs |
| Filtre par module | Sélection du module source (AUTH, ERROR, INFO, ...) |
| Filtre par date | Sélection d'une date précise |
| Coloration par module | ERROR=rouge, WARNING=jaune, INFO=vert, DEBUG=violet, AUTH=bleu clair |
| Panneau détails | Affichage formaté de la ligne sélectionnée (clic sur une ligne) |
| Onglet Lignes invalides | Lignes non parsées avec affichage du format attendu |
| Avertissement format | QMessageBox si aucun fichier valide trouvé dans le dossier |
| Thèmes | 5 thèmes de couleur accessibles via le bouton Paramètres |

**Aucune dépendance avec le reste du projet** — `admin.py` peut être copié et utilisé seul.

---

## Format des logs

Les fichiers sont générés automatiquement par `shared/logging/file_logger.py` dans le dossier `logs/`.

**Nom de fichier :**
```
log-AAAA-MM-JJ.txt
Exemple : log-2024-03-15.txt
```

**Format de chaque ligne :**
```
HH:MM = [MODULE] message libre
```

Exemples :
```
14:32 = [AUTH] Connexion utilisateur réussie
09:01 = [ERROR] Fichier introuvable : data.xlsx
10:15 = [INFO] 3 fichiers chargés, 1247 enregistrements
22:47 = [WARNING] Feuille vide ignorée : Sheet2
```

Les modules courants sont : `INFO`, `ERROR`, `WARNING`, `DEBUG`, `AUTH`, `CHART`, `EXPORT`, `SESSION`.

Toute ligne ne respectant pas ce format exactement est classée dans l'onglet **Lignes invalides** de l'outil admin, avec le format attendu affiché en dessous pour faciliter le diagnostic.

---

## Thèmes et personnalisation

### Application principale
Les thèmes sont gérés par `presentation/theme/theme_manager.py` (Singleton). La palette de couleurs est définie dans `shared/constants.py` (dictionnaire `C`).

Changer le thème : **Page Paramètres** → section Thème → sélectionner et appliquer.

### Outil Admin
Cliquer sur **Paramètres** (barre du haut) pour ouvrir le dialogue de sélection de thème.

| Thème Admin | Description |
|---|---|
| Bleu nuit | Fond sombre bleu — thème par défaut |
| Vert forêt | Fond sombre vert |
| Violet nuit | Fond sombre violet |
| Rouge sombre | Fond sombre rouge |
| Clair | Fond blanc — pour environnements lumineux |

---

## Sessions et préférences

À chaque lancement, l'application restaure automatiquement la dernière session (fichiers chargés, filtres actifs). Les préférences (thème, colonnes visibles) sont persistées séparément.

Fichiers JSON stockés dans :
```
Windows  : %APPDATA%\StuGoCO2\
Linux/Mac: ~/.local/share/StuGoCO2/
```

Pour réinitialiser : **Page Paramètres** → "Effacer la session".

---

## Patterns de conception utilisés

| Pattern | Emplacement |
|---|---|
| Singleton | `ThemeManager`, `ActionLogger`, `DataService`, `SessionRepository`, `EventBus` |
| Observer | `EventBus` (publish/subscribe), signal `theme_changed` |
| Command + Memento | `Command`, `CommandHistory` — undo/redo |
| Strategy | `Renderer2D`, `Renderer3D`, `ExtractorFactory` |
| Façade | `MainWindow`, `DataService`, `ChartService` |
| Médiateur | `UIMediator`, `MainWindow` |
| Template Method | `BasePage`, widgets primitifs |
| Adaptateur | `PandasModel` (pandas → Qt MVC) |
| Builder | `StylesheetBuilder` |
| Factory | `RendererFactory`, `ExtractorFactory`, `WidgetFactory` |
| Value Object | `ChartConfig`, `ColorValue` |
| Module Singleton | `shared/constants.py` (`C`, `ZONES`), `shared/scaling.py` (`S`) |

---

## Notes pour les développeurs

- **Toutes les tailles UI passent par `S`** — ne jamais coder de pixels en dur. Utiliser `S.font_base`, `S.btn_h`, `S.sp(n)`.
- **Toutes les couleurs passent par `C`** — ne jamais écrire de codes couleur directement dans les widgets. Les modifier dans `shared/constants.py`.
- **Ajouter une page** : créer `presentation/pages/ma_page/ma_page.py` héritant de `BasePage`, enregistrer dans `PAGES` (constants), ajouter à `MainWindow` et à la `Sidebar`.
- **Ajouter un type de graphique** : ajouter dans `CHART_TYPES` (constants), implémenter la stratégie dans `rendering/strategies/`, enregistrer dans `rendering/factory.py`.
- **Logger une action** : utiliser `shared/logging/file_logger.py` — `log_msg("MODULE", "message")` ou `log_error("MODULE", "message")`.
