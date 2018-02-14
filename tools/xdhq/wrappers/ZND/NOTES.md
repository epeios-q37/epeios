# Notes concernant la version *PHP* de *UnJSq*/*XDHq*

## Lancement

### *Cygwin*

*UnJSq* (`UnJSq/ZND/UnJSq.php`) lance un serveur web via *node.js*, qui est normalement interrompu lors d'un *CTRL-C*, mais cela ne fonctionne pas sous *Cygwin*. Il faut donc lancer le programme sous une session *DOS* classique.

Si lanc� directement (et non pas � l'aide de la commande ci-dessous) sous *Cygwin*, il faudra tuer le serveur *httpd* manuellement.

Pour contourner ce probl�me, lancer avec de la mani�re suivante :  `cmd /c start php ...`.

*NOTA*: dans un des r�pertoire du *PATH*, il y a un fichier `php.bat`avec le contenu suivant :

``` batch
 h:/php-src/x64/Release_TS/php.exe %*
 ```
