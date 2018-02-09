 # Notes concernant la version *Java* (*JRE*) de *UnJSq*/*XDHq*

 ## Compilation

 Script pour *recompiler* l'ensemble des sources *JAVA* (*attention*: le r�pertoire `classes` **doit** exister !) :

 `pushd /cygdrive/h/hg/epeios/tools/jreq;rm -rf classes/*;javac -d classes *.java;cd /cygdrive/h/hg/epeios/tools/xdhq/wrappers/JRE;rm -rf classes/*;javac -d classes *.java;cd /cygdrive/h/hg/epeios/tools/xdhq/UnJSq/JRE;rm -rf classes/*;javac -d classes *.java;popd`

 Il y a �galement des sources dans `tools/xdhq/UnJSq/JRE`, mais elles ne devraient pas avoir � �tre modifi�s.
 
 ## Lancement

 ### *Cygwin*

 *UnJSq* (`info.q37.unjsq.UnJSq`) lance un serveur web via *node.js*, qui est normalement interrompu lors d'un *CTRL-C*, mais cela ne fonctionne pas sous *Cygwin*. Il faut donc lancer le programme sous une session *DOS* classique.

 Si lanc� directement (et non pas � l'aide de la commande ci-dessous) sous *Cygwin*, il faudra tuer le serveur *httpd* manuellement.

 Pour contourner ce probl�me, lancer avec de la mani�re suivante :
  * pour lancer uniquement : `cmd /c start java <class>`,
  * pour compiler puis lancer en cas de succ�s : `javac *.java >&1 | head && cmd /c start java <class>`.

 ### `CLASSPATH` pour le d�veloppement

 `.;h:/hg/epeios/tools/jreq/classes/;h:/hg/epeios/tools/xdhq/wrappers/JRE/classes/;h:/hg/epeios/tools/xdhq/UnJSq/JRE/classes/`