Files in this directory are directly red by the httpd server ; the 'xdhbrwq' tool doesn't read them.

----

FOR THE MAINTAINER :

Cr�er un lien ('mklink /j') en tant qu'administrateur � partir du r�pertoire 'htdocs' de l'installation d'Apache vers ce r�pertoire.
Ex : 'C:\Program Files (x86)\Apache Software Foundation\Apache2.2\htdocs>mklink /j xdh h:\hg\epeios\tools\xdhbrwq\httpd\htdocs'

Le r�pertoire 'js' est un 'mklink /j' vers le r�pertoire de m�me nom dans 'corpus'.