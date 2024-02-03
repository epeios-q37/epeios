# Notes à propos de ce projet

## Introduction

Ce projet concerne la version [*Brython*](httpd://brython.info) du *toolkit* *Atlas*.

*Brython* permet d'exécuter du code *Python* dans le navigateur.

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

Lorsque *index.php" est chargé dans ue *iframe*, il faut lui ajouter `allow="web-share"`.


## Scripts dans le *head*

Pour pouvoir être pris en charge par *Brython*, le code python est placé tel quel dans un élément *script*. Si le code source *Python* contient la chaîne `</script>`, comme cela peut être le cas lorsque l'utilisateur définit un contenu pour la section *head*, le script censé contenir le code *Python* s'interrompt au niveau de cette chaîne et tout le code *python* qui suit est ignoré, entraînant une erreur de syntaxe. *CDATA* ne peut être utilisé dans ce contexte car ignoré sans un élément *script*. C'est pour cela que la chaîne `</script>` est remplacé par la chaîne `_BrythonWorkaroundForClosingScriptTag_` au niveau PHP, puis rétablie au niveau *Python*.

## Serveur

### Prérequis

Comme il n'y a pas de *socket* dans les APIs disponibles avec les navigateurs Web, on va utiliser les *websockets* pour se connecter au serveur *FaaS*. On ne peut pas se connecter  directement au serveur *FaaS* avec une *websocket*, car il y a un protocole particulier. On va donc passe par un l'utilitaire *websocketd* combiné à *socat*.

*websocketd* est disponible dans les dépôts *Ubuntu*, mais pas *Debian*. Pour ce dernier, il faut donc récupérer l'utilitaire directement sur le site dédié. L'utilitaire est un simple exécutable fournit dans un *ZIP*.

*socat* est installé par défaut sur *Ubuntu*, mais doit être installé à partir du dépôt avec *Debian*.

On se connecte à *websocktd* via *nginx*, qui prend en chargele protocole *SSL*/*TTL*, raison pour laquelle on n'utilse pas les options `--ssl` et consort de *websocketd*. Voici la partie de la configuraiton dédié à *nfingx*.

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

L'ensemble est lancé de la manière suivante : `websocketd --binary=true  --port=8080  socat - TCP4:localhost:53700`



### Mise en place

Contenu du fichier `/etc/systemd/system/faasws.service` :

```systemd
[Unit]
Description=WebSocket connection to Atlas FaaS daemon
After=network.target

[Service]
User=root
ExecStart=/usr/bin/websocketd --ssl --sslcert=/var/lib/dehydrated/certs/q37.info/fullchain.pem --sslkey=/var/lib/dehydrated/certs/q37.info/privkey.pem --binary=true  --port=8080  socat - TCP4:localhost:53700
Restart=always

[Install]
WantedBy=multi-user.target
```

Enregistrement du service : `systemctl enable faasws.service`

## Licenses

- *Ace* (éditeur en ligne) : voir https://github.com/ajaxorg/ace/blob/master/LICENSE (semble être une license BSD) ;
- *Brython* : *BSD 3-Clause "New" or "Revised" License* (https://github.com/brython-dev/brython/blob/master/LICENCE.txt) ;
- https://github.com/feross/buffer (émulation du *Buffer* de *Node.js* dans un navigateur) : *MIT* (https://github.com/feross/buffer/blob/master/LICENSE) ;
- *blob-to-buffer* : *MIT* (https://github.com/feross/blob-to-buffer/blob/master/LICENSE) ;
- *toolkit* *Atlas* :-) : *MIT*.