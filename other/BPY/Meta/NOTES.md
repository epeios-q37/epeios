# À propos de ce répertoire

Contient les applications qui sont communes à *Brython* et *Python*.

Pour lancer la version *Brython* : `BPYB_Launch <app_dir>`.
Pour lancer la version *Python* : `BPYP_Launch <app_dir>`.

## Paramètre `useUCUqDemoDevices`

Le paramètre `useUCUqDemoDevices` de *Libs/htdocs/index.php* permet de rajouter *True* comme dernier arguments d'un appel à *ucuq.ATKConnect(…)*, ce qui permet d'utiliser les kits définis dans *ATK_Admin* lorsque le fichier de configuration utilisé par *UCUq* n'est pas défini.

Utilisé dans les d"mos de la page consacré à *UCUq* pour le site *ng.q37.info* (voir *ucuq.js*).

## Aide pour générer les macros pour la'application *Servos*

Sélectionner les macros et puis sélectionner *Run Command* à partir du menu contextuel.

LEs scripts sont gérés par l'extension *VSCode* *Command runner* et définis dans le *workspace* du projet.
