# Page d'aide : explique chaque fonctionnalite de l'application, regroupee par section

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt

from shared.constants import C
from shared.scaling import S
from presentation.theme.theme_manager import ThemeManager


SECTIONS = [
    {
        "icon": "↑",
        "title": "Importer des fichiers",
        "items": [
            ("Formats acceptes", "Fichiers Excel (.xlsx, .xls) exportes depuis le logiciel de mobilite. Chaque onglet correspond a une faculte."),
            ("Ajouter des fichiers", "Cliquez sur le bouton + ou glissez vos fichiers dans la zone d'import. Plusieurs fichiers peuvent etre charges simultanement."),
            ("Supprimer un fichier", "Dans la liste des fichiers importes, cliquez sur la corbeille a droite du fichier pour le retirer de l'analyse."),
            ("Colonnes requises", "Le fichier doit contenir au minimum : pays, nb_etudiants, total_tco2, zone. Les colonnes manquantes sont ignorees silencieusement."),
            ("Mise a jour automatique", "Apres chaque import ou suppression, tous les graphiques et le tableau se mettent a jour instantanement."),
        ],
    },
    {
        "icon": "≡",
        "title": "Tableau de donnees",
        "items": [
            ("Tri des colonnes", "Utilisez le selecteur 'Trier par' en haut du tableau pour choisir la colonne de tri. Le bouton fleche inverse l'ordre (croissant / decroissant)."),
            ("Export CSV", "Le bouton 'Export CSV' sauvegarde les donnees actuellement affichees (apres filtres) dans un fichier .csv."),
            ("Filtres actifs", "Le tableau reflete toujours les filtres actifs dans la barre laterale gauche. Reinitialiser les filtres pour voir toutes les donnees."),
            ("Colonnes affichees", "Pays, Faculte, Zone CO2, Nb etudiants, Total tCO2e, tCO2e par voyage, Source du fichier."),
        ],
    },
    {
        "icon": "◈",
        "title": "Graphiques",
        "items": [
            ("Types disponibles", "Barres verticales, Barres horizontales, Camembert, Donut, Aires empilees, Treemap. Chaque type met en valeur un aspect different des donnees."),
            ("Axe X", "Choisissez la dimension a analyser : Faculte, Zone geographique ou Pays."),
            ("Axe Y (Valeur)", "Total tCO2e (emissions globales), Nb etudiants ou tCO2e par voyage (intensite par deplacement)."),
            ("Couleur (groupe)", "Colorier les barres par Faculte, par Zone ou sans regroupement. Affecte la lisibilite selon le type de graphique."),
            ("Top pays", "Limite l'affichage aux N premiers pays (boutons + / -). Utile pour les graphiques Camembert ou Barres avec beaucoup de pays."),
            ("Mode 3D", "Bascule entre vue 2D et 3D. En 3D, les curseurs d'elevation et d'azimut permettent de faire pivoter le graphique."),
            ("Export PNG", "Sauvegarde le graphique courant en image haute resolution (.png)."),
        ],
    },
    {
        "icon": "⊞",
        "title": "Comparaison multi-fichiers",
        "items": [
            ("Principe", "La page Comparaison affiche simultanement les graphiques de chaque fichier importe, cote a cote ou en grille."),
            ("Mode d'affichage", "Grille par fichier : un graphique par fichier. Cote a cote : meme type pour tous. Empile par fichier : superposition verticale."),
            ("Colonnes", "Le bouton + / - ajuste le nombre de colonnes (1 a 5) dans la disposition en grille."),
            ("Export groupee", "Le bouton PNG exporte tous les graphiques visibles en une seule image composite."),
        ],
    },
    {
        "icon": "▤",
        "title": "Filtres (barre laterale)",
        "items": [
            ("Faculte", "Cochez ou decochez les facultes a inclure dans l'analyse. Toutes sont activees par defaut."),
            ("Zone CO2", "Filtrez par zone geographique (Zone 1 a 5). Chaque zone correspond a un rayon de distance et une couleur."),
            ("Recherche pays", "Tapez le nom d'un pays (ou une partie) pour filtrer sur ce pays uniquement."),
            ("Nb etudiants (Min / Max)", "Limitez l'analyse aux facultes ayant un nombre d'etudiants dans la plage definie. Cliquez + / - ou tapez la valeur directement."),
            ("Total tCO2e (Min / Max)", "Meme principe pour les emissions : filtrez par seuil minimum et maximum."),
            ("Masquer les zeros", "Exclut les lignes avec 0 etudiant (souvent des erreurs ou des donnees manquantes)."),
            ("Reinitialiser", "Le bouton 'Reinit.' remet tous les filtres aux valeurs initiales."),
        ],
    },
    {
        "icon": "⚙",
        "title": "Parametres",
        "items": [
            ("Themes predefinies", "Cliquez sur un theme pour l'appliquer instantanement a toute l'interface. Le theme est sauvegarde automatiquement."),
            ("Preset personnalise - 2 cles", "Choisissez uniquement le fond principal et la couleur d'accent : toute la palette est calculee automatiquement."),
            ("Preset personnalise - 6 cles", "Definissez 6 couleurs de base (fonds, texte, accent). Les 12 autres sont derivees automatiquement."),
            ("Preset personnalise - 18 cles", "Controle total : definissez chaque couleur de l'interface independamment."),
            ("Sauvegarder / Charger un preset", "Exportez votre palette en .json pour la partager ou la recharger plus tard. Les presets sont stockes dans %LOCALAPPDATA%\\StuGoCO2\\PresetColors\\"),
            ("Curseur", "Changez l'apparence du curseur de la souris. Option 'Image personnalisee' pour utiliser votre propre fichier .png ou .ico."),
            ("Effacer la session", "Supprime les donnees de session (fichiers charges, etat des filtres). L'application repart a zero au prochain lancement."),
        ],
    },
]


class HelpPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.restyle()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.margin_page, S.margin_page, S.margin_page, S.margin_page)
        lay.setSpacing(S.spacing_md)

        self.title = QLabel("Aide")
        self.sub   = QLabel("Guide d'utilisation de StuGo CO2 Explorer v7.0")
        lay.addWidget(self.title)
        lay.addWidget(self.sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        il = QVBoxLayout(inner)
        il.setContentsMargins(0, S.spacing_sm, S.spacing_md, S.spacing_lg)
        il.setSpacing(S.spacing_lg)

        self.section_widgets = []

        for section in SECTIONS:
            card = self.make_section(section)
            self.section_widgets.append(card)
            il.addWidget(card)

        il.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll, 1)

    def make_section(self, section: dict) -> QWidget:
        card = QFrame()
        card.setObjectName("help_card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(S.margin_card + 4, S.margin_card, S.margin_card + 4, S.margin_card)
        cl.setSpacing(S.spacing_sm)

        header = QHBoxLayout()
        header.setSpacing(S.spacing_sm)
        icon_lbl = QLabel(section["icon"])
        icon_lbl.setObjectName("help_icon")
        title_lbl = QLabel(section["title"])
        title_lbl.setObjectName("help_section_title")
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl, 1)
        cl.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("help_sep")
        cl.addWidget(sep)

        for label, desc in section["items"]:
            row = QWidget()
            row.setObjectName("help_row")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(S.spacing_md)

            dot = QLabel("▸")
            dot.setFixedWidth(round(S.dpi_scale * 12))
            dot.setObjectName("help_dot")
            dot.setAlignment(Qt.AlignmentFlag.AlignTop)

            lbl_key = QLabel(label)
            lbl_key.setObjectName("help_key")
            lbl_key.setFixedWidth(round(S.dpi_scale * 180))
            lbl_key.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            lbl_val = QLabel(desc)
            lbl_val.setObjectName("help_val")
            lbl_val.setWordWrap(True)
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            rl.addWidget(dot)
            rl.addWidget(lbl_key)
            rl.addWidget(lbl_val, 1)
            cl.addWidget(row)

        return card

    def restyle(self) -> None:
        self.title.setStyleSheet(f"font-size:{S.font_hero - 4}px;font-weight:800;color:{C['text_primary']};")
        self.sub.setStyleSheet(f"font-size:{S.font_base}px;color:{C['text_secondary']};margin-bottom:{S.spacing_sm}px;")
        card_qss = (
            f"QFrame#help_card{{background:{C['bg_card']};border:1px solid {C['border']};border-radius:{S.r_md()}px;}}"
            f"QLabel#help_icon{{color:{C['accent']};font-size:{S.font_xl}px;background:transparent;}}"
            f"QLabel#help_section_title{{color:{C['text_primary']};font-size:{S.font_md}px;font-weight:700;background:transparent;}}"
            f"QFrame#help_sep{{background:{C['border']};border:none;max-height:1px;}}"
            f"QLabel#help_dot{{color:{C['accent']};font-size:{S.font_sm}px;background:transparent;}}"
            f"QLabel#help_key{{color:{C['text_primary']};font-size:{S.font_sm}px;font-weight:600;background:transparent;}}"
            f"QLabel#help_val{{color:{C['text_secondary']};font-size:{S.font_sm}px;background:transparent;}}"
            f"QWidget#help_row{{background:transparent;}}"
        )
        self.setStyleSheet(card_qss)
