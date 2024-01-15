# Notes au sujet de ce répertoire

Répertoire pour tester de *Brython* et son utilisation avec le *toolkit* *Atlas*.

## Code à ajouter aprés celui généré par *browserify*

```js
atlastk = require("atlastk")

var $module = {
    call: atlastk.call,
    launch: atlastk.launch,
    standBy: atlastk.standBy,
    getCallbackBundle: atlastk.getCallbackBundle,
    broadcastAction: atlastk.broadcastAction,
}
```

## Divers

Parce que l'inclusion de fichier ne gère pas la protocole `file:`, ces fichier doivent être servis avec un serveur *http*.

Pour *nginx*, ajouter dans la section *server* :

```nginx
	location /brython {
		alias /media/csimon/H/hg/epeios/other/brython;
	}
```

Mettre le chemin réel, pas celui derrière un lien symbolique.

Attention, tous les répertoires de l'alias doivent être en exécution !

## Licenses

- *Ace* (éditeur en ligne) : voir https://github.com/ajaxorg/ace/blob/master/LICENSE (xemble être une license BSD) ;
- *Brython* : *BSD 3-Clause "New" or "Revised" License* (https://github.com/brython-dev/brython/blob/master/LICENCE.txt) ;
- https://github.com/feross/buffer (émulation du *Buffer* de *Node.js* dans un navigateur) : *MIT* (https://github.com/feross/buffer/blob/master/LICENSE) ;
- *blob-to-buffer* : *MIT* (https://github.com/feross/blob-to-buffer/blob/master/LICENSE) ;
- *toolkit* *Atlas* :-) : *MIT*.

## Version *Brython* (*BRY*) du *toolkit* *Atlas*

La version *Brython* du *toolkit* *Atlas* s'appuie sur sa version *Node.js* (*NJS*). Cette dernière utilise le module *Buffer* natif de *Node.js*, qui n'est pas implémenté dans les navigateurs.


## Redirection de l'affichage de la console vers un élément HTML

https://stackoverflow.com/questions/20256760/javascript-console-log-to-html

```js
(function () {
    var old = console.log;
    var logger = document.getElementById('log');
    console.log = function (message) {
        if (typeof message == 'object') {
            logger.innerHTML += (JSON && JSON.stringify ? JSON.stringify(message) : message) + '<br />';
        } else {
            logger.innerHTML += message + '<br />';
        }
    }
})();
```
 