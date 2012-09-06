Deployment
==========

Process
~~~~~~~

Drei Instanzen auf dem Server:

- snapshot.youarehero.net (wird automatisch aus dem git gebaut) [master], wird alle ??? geupdated, tests gelaufen, docs gebaut, ...
- staging.youarehero.net (kann per fabric script aus bestimmter revisionsid gebaut werden [auch tests etc])
- youarehero.net (live version) [production]

Alle Entwicklung passiert in der master branch.
Release funktioniert so:
1. Fuer Release gewuenschte Inhalte aus Master in staging mergen. dazu wird der
 aktuelle produktion stand genommen, alle aenderungen eingepfelgt
2. tests laufen lassen und ueberpruefen ob alles gut aussieht
3. entsprechende revision in staging als release taggen (z.b.release142)
4. release142 in production mergen