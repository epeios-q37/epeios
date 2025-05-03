# À propos de ce répertoire

NOTA : il n'y a pas de dépôt dédié pout *Blocky*.

## Description

Ce répertoire contient les fichiers de l'environnement *Blockly* pour manipuler des fichier.
Lien vers l'environnement en local : <http://localhost/blockly?lang=fr>.

- Pour construire les fichiers web (stockés dans ~/ATK/BLY/web) : `BLY_Build` ;
- pour tester (construit les fichiers et les lance le navigateur) : `BLY_Launch` ;
- pour publier sur le web (lancer auparavant `BLY_Build`) : `BLY_Publish` ;
- les démos sont cherchés dans <https://raw.githubusercontent.com/epeios-q37/epeios/refs/heads/master/other/BLY/examples/>.

Resources :

- création de blocs : <https://google.github.io/blockly-samples/examples/developer-tools/index.html> ;
- à propos des *shadow blocks* : <http://bekawestberg.me/blog/shadows-1/>
  - le lien vers le point 3 pointe vers le point 2 ; il faut taper le `3` dans l'URL,
- *Blockly* en ligne : <https://blockly-demo.appspot.com/static/demos/code/index.html>.

## Code XML

Le code source d'un « programme » *Blockly* est au format *XML* (peut aussi être du *JSON*). Il est passé compressé/base64/URI (voir le paramètre *code* de *BPY* pour plus de détail).
NOTA : le code source au format *XML* se compresse mieux que celui au format *JSON*.
