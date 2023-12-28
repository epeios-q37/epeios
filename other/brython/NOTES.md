# Notes au sujet de ce répertoire

Test de *Brython*

Parce que l'inclusion de fichier ne gère pas la protocole `file:`, ces fichier doivent être servis avec un serveur *http*.

Pour *nginx*, ajouter dans la section *server* :

```nginx
	location /brython {
		alias /media/csimon/H/hg/epeios/other/brython;
	}
```

Mettre le chemin réel, pas celui derrière un lien symbolique.

Attention, tous les répertoires de l'alias doivent être en exécution !
