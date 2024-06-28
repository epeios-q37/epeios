# Notes à propos de la version *Brython* du *toolkit* *Atlas*

## Introduction

Ce projet concerne la version [*Brython*](httpd://brython.info) du *toolkit* *Atlas*.

*Brython* permet d'exécuter du code *Python* dans le navigateur. Sert à exécuter une application basée sur le *toolkit* *Atlas* dans le navigateur (site *Zelbinium*, démonstration en ligne du *toolkit* *Atlas*).

Si modification code, voir pour mise à jour *Zelbinium* (`ZLBRTW`). Les applications d'exemple, ainsi que le dépôt *brython*, sont utilisés pour la section *Inspiration* du site *Zelbinium*.

## Installation

`ATKBRYBuild` browserifie le fichier *atlastk.js* et place tous les fichiers nécessaires dans `/home/csimon/ATK/BRY/web`. Il y a un lien symbolique de `/var/www/brython` vers ce répertoire.

`ATKBRYPublish` met le contenu (avec ajout du *HOSTNAME*) sur le serveur adéquat. Il faut lancer `ATKBRYBuild` auparavant.

## Paramètres

Le fichier `TestIframe.html` est un fichier contenant *Brython* dans une *iframe*. Sert à tester si l'ouverture dans un nouvel onglet récupère le contenu de l'éditeur.

Au script `index.php`, on peut passer les paramètres suivants :
- `demo` : nom de la démo à précharger ;
- `code` : code source *Python* à placer dans l'éditeur ; ne pas utiliser en même temps que le paramètre `demo` ;
- `cursor` : si `code` présent et non vide, position du curseur dans l'éditeur, sous la forme `<ligne>,<colonne>`, avec `0,0` comme origine ; donne également le docus à l'éditeur.

## Détection de *await* sans *async* et vice-versa

L'extension *Pylance* détecte par défaut les fonction utilisant *await* sans être *async*.

Pour détecter les coroutines appelées sans *await*, ajouter cela dans le fichier de configuration de *Pylance* (*settings.json*)

```json
"python.analysis.diagnosticSeverityOverrides": {
    "reportUnusedCoroutine": "error"
}
```

## Fonction de copie ou de partage

Actuellement, la copie et le partage de l'application via les boutons fonctionnent probablement parce que *Brython* et les applications sont dans le même domaine. Si ce ne devait plus être le cas, il faudra probablement ajouter l'attribut `allow` aux *iframes*, avec un contenu genre `web-share; clipboard-write` (pas testé).

Lorsque *index.php* est chargé dans une *iframe*, il faut lui ajouter `allow="web-share"`.

## Échappement de caractères dans le code source *Python*

### Code source contenant un `` ` `` (*backquote*)

Le script *PHP* `index.php` génère un script *JavaScript* dans lequel le code source *Python* est stocké dans une variable comme une chaîne multi-ligne, c'est-à-dire délimitée par des *backquotes* (`` ` ``). Tout *backquote* contenu dans le code source *Python* interromprait donc prématurément la chaîne multi-ligne.

Pour éviter cela, il faut remplacer chaque *backquote* dans le code source *Python* par la chaîne `_BrythonWorkaroundForBackQuote_`. Le code *JavaScript* généré par le script *PHP* remplace cette chaîne par un *backquote* juste avant que le code source *Python* ne soit passé à l'éditeur *Ace*.

### Code source contenant un `'` (apostrophe)

Même remarque que précédemment. Les apostrophes ont apparemment un rôle dans les chaînes multi-lignes.

La chaîne d'échappement est : `_BrythonWorkaroundForSingleQuote_`.

### Scripts dans le *head*

Pour pouvoir être pris en charge par *Brython*, le code python est placé tel quel dans un élément *script*. Si le code source *Python* contient la chaîne `</script>`, comme cela peut être le cas lorsque l'utilisateur définit un contenu pour la section *head*, le script censé contenir le code *Python* s'interrompt au niveau de cette chaîne et tout le code *python* qui suit est ignoré, entraînant une erreur de syntaxe. *CDATA* ne peut être utilisé dans ce contexte car ignoré sans un élément *script*. C'est pour cela que la chaîne `</script>` est remplacé par la chaîne `_BrythonWorkaroundForClosingScriptTag_` au niveau PHP, puis rétablie au niveau *Python*.

## Serveur

### Prérequis

Comme il n'y a pas de *socket* dans les APIs disponibles avec les navigateurs Web, on va utiliser les *websockets* pour se connecter au serveur *FaaS*. On ne peut pas se connecter  directement au serveur *FaaS* avec une *websocket*, car il y a un protocole particulier. On va donc passe par un l'utilitaire relayant une connection issu s'une *websocket* vers le serveur *Faas*. *websocketd* combiné à *socat*.


#### *nginx*

On peut se connecter directement à l'utilitaire faisant la passerelle entre les *websockets* et le serveur *FaaS* (*websocat* ou *websocketd*), mais la connexion se fait sur un autre port que `443` (*https*), ce qui peut (va) poser problème avec certains *proxy*, et l'utilitaire doit prendre en charge la gestion de *TLS*.

En utilisant *nginx*, on peut se connecter au serveur *FaaS* via l'utilitaire faisant passerelle avec le port standard *https* `443`, et c'est *ngins* qui va pendre en charge *TLS*.

Voici la configuration *nginx* correspondante :

```init
# This section is common for all websockets

map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

# Section for the handling of *Brython*

upstream faas {
    server localhost:8080;
}

server {
  …


  location /faas/ {
    proxy_pass http://faas;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    proxy_set_header Host $host;
    proxy_read_timeout 15m;
  }  
}
```

#### Utilisation de *websocat*

*websocat* se trouve à et doit être téléchargé à partir de <https://github.com/vi/websocat> (c'est directement l'exécutable à renommer et à placer dans le path (`/usr/bin/`)).

Utilisation : `websocat -b ws-l:127.0.0.1:8080 tcp:localhost:53700`

Le message d'information suivant s'affiche :

> websocat: Unfortunately, serving multiple clients without --exit-on-eof (-E) or with -U option is prone to socket leak in this websocat version

Cependant, à la lecture de l'*issue* suivante, cela ne semble pas poser problème :

https://github.com/vi/websocat/issues/183

#### Utilisation de *websocketd* en combinaison avec *socat*

**NOTA** : non utilisé au profit de la solution ci-dessus à cause d'n problème de fuite mémoire de *websocketd*. En outre, la solution ci-dessus est développé en *Rust* programma compile, alors que *websocketd* est développé en *Go*, et la solution ci-dessus n'a pas besoin de *socat*.

*websocketd* est disponible dans les dépôts *Ubuntu*, mais pas *Debian*. Pour ce dernier, il faut donc récupérer l'utilitaire directement sur le site dédié. L'utilitaire est un simple exécutable fournit dans un *ZIP*.

*socat* est installé par défaut sur *Ubuntu*, mais doit être installé à partir du dépôt avec *Debian*.

On se connecte à *websocktd* via *nginx*, qui prend en charge le protocole *SSL*/*TTL*, raison pour laquelle on n'utilse pas les options `--ssl` et consort de *websocketd*. Voici la partie de la configuraiton dédié à *ngingx*.

L'ensemble est lancé de la manière suivante : `websocketd --binary=true  --port=8080  socat - TCP4:localhost:53700`


### Mise en place

Contenu du fichier `/etc/systemd/system/faasws.service` :

Version *websocat* :

```systemd
[Unit]
Description=WebSocket connection to Atlas FaaS daemon
After=network.target

[Service]
User=root
ExecStart=/usr/bin/websocat -b ws-l:127.0.0.1:8080 tcp:localhost:53700
Restart=always

[Install]
WantedBy=multi-user.target
```


Version *websocketd*/*socat* (non utilisée) :

```systemd
[Unit]
Description=WebSocket connection to Atlas FaaS daemon
After=network.target

[Service]
User=root
ExecStart=/usr/bin/websocketd --binary=true  --port=8080 socat - TCP4:localhost:53700
Restart=always

[Install]
WantedBy=multi-user.target
```

Enregistrement du service : `systemctl enable faasws.service`

## Licenses

- *Ace* (éditeur en ligne) : voir https://github.com/ajaxorg/ace/blob/master/LICENSE (semble être une license BSD) ;
- *Brython* : *BSD 3-Clause "New" or "Revised" License* (https://github.com/brython-dev/brython/blob/master/LICENCE.txt) ;
- *toolkit* *Atlas* :-) : *MIT*.