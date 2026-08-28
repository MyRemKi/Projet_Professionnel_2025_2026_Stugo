; installer.iss
; Script Inno Setup 6 pour StuGo CO2 Explorer v7.0
; Installation par utilisateur — aucun droit administrateur requis

#define AppName      "StuGo CO2 Explorer"
#define AppShortName "StuGo"
#define AppVersion   "7.0"
#define AppPublisher "StuGo"
#define AppExe       "StuGoCO2_Explorer.exe"
#define AdminExe     "Admin_Logs.exe"
#define SourceDir    "dist\StuGoCO2"
#define DataDir      "{localappdata}\StuGoCO2"

[Setup]
AppId={{8F3A2C1D-4E5B-4F6A-9D0E-1C2B3A4D5E6F}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppComments=Analyse et visualisation des emissions CO2 de mobilite etudiante

; Installation dans le dossier local de l'utilisateur — sans droits admin
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}

; Aucun droit administrateur requis
PrivilegesRequired=lowest

AllowNoIcons=no
LicenseFile=
InfoBeforeFile=setup_info.txt
OutputDir=dist
OutputBaseFilename=StuGoCO2_Setup_v7.0
SetupIconFile=assets\setup_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
UsedUserAreasWarning=no
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayName={#AppName} v{#AppVersion}
UninstallDisplayIcon={app}\{#AppExe}
DisableProgramGroupPage=no
ShowLanguageDialog=auto
LanguageDetectionMethod=uilanguage
SetupMutex=StuGoCO2_Setup_Mutex

[Languages]
Name: "french";  MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
french.AppIsRunning=StuGo CO2 Explorer est en cours d'execution.%nFermez l'application avant de continuer l'installation.
french.WelcomeText=Ce programme va installer {#AppName} v{#AppVersion} sur votre ordinateur.%n%nL'installation s'effectue dans votre dossier personnel, sans droits administrateur.%n%nFermez toutes les applications ouvertes avant de continuer.
english.AppIsRunning=StuGo CO2 Explorer is running.%nClose it before continuing the installation.
english.WelcomeText=This will install {#AppName} v{#AppVersion} on your computer.%n%nThe installation is performed in your personal folder, no administrator rights required.%n%nClose all running applications before continuing.

[Tasks]
Name: "desktopicon"; Description: "Creer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Files]
; Mode onedir : exe + dossier _internal partage (demarrage instantane)
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Demarrer
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExe}"; Comment: "Analyser les emissions CO2 de mobilite etudiante"
Name: "{group}\Desinstaller {#AppName}"; Filename: "{uninstallexe}"

; Bureau (optionnel)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Registry]
; Cle utilisateur uniquement — jamais HKLM
Root: HKCU; Subkey: "Software\{#AppPublisher}\{#AppName}"; \
    ValueType: string; ValueName: "InstallPath"; \
    ValueData: "{app}"; Flags: uninsdeletekey

Root: HKCU; Subkey: "Software\{#AppPublisher}\{#AppName}"; \
    ValueType: string; ValueName: "Version"; \
    ValueData: "{#AppVersion}"; Flags: uninsdeletevalue

[Run]
; Proposer de lancer l'application a la fin de l'installation
Filename: "{app}\{#AppExe}"; \
    Description: "Lancer {#AppName} maintenant"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// ── Desinstallation : proposer de supprimer les donnees utilisateur ───────────
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir : String;
  Answer  : Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\StuGoCO2');
    if DirExists(DataDir) then
    begin
      Answer := MsgBox(
        'Voulez-vous supprimer vos donnees personnelles ?' + #13#10 +
        '(' + DataDir + ')' + #13#10#13#10 +
        'Cela supprimera : sessions, logs, presets de couleurs et preferences.',
        mbConfirmation, MB_YESNO
      );
      if Answer = IDYES then
        DelTree(DataDir, True, True, True);
    end;
  end;
end;
