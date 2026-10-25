# Construire une app desktop simple (et la terminer) : 9 leçons tirées de Clarionet

Quand j’ai commencé **Clarionet** (une app Linux minimaliste pour écouter la radio en ligne), je pensais surtout au résultat.  
Avec le recul, le plus intéressant, c’est la méthode que le projet m’a forcé à adopter.

Si tu construis un side-project, une app desktop, ou un petit produit open source, voici les leçons les plus utiles que j’aurais aimé formaliser plus tôt.

## 1) Le MVP doit valider l’usage, pas la vision finale

Mon premier objectif n’était pas d’avoir une “belle app”.  
C’était d’avoir une app qui fait le job sans friction : lancer, choisir une station, écouter.

**Concrètement :**
- stack simple et robuste (`Python`, `GTK3/PyGObject`, `mpv`),
- fonctionnalités de base d’abord (lecture, volume, navigation, état),
- pas d’optimisation prématurée.

**Leçon :** tant que l’usage principal n’est pas fluide, tout le reste est secondaire.

---

## 2) La simplicité est une contrainte active, pas un manque d’ambition

“Minimaliste” est facile à dire, difficile à exécuter.  
À chaque itération, j’avais le choix entre ajouter une option… ou enlever une friction.

**Cadre utile :**
- chaque feature doit répondre à un problème réel d’usage,
- chaque élément UI doit avoir une raison d’être visible,
- chaque complexité ajoutée doit avoir un coût assumé.

**Leçon :** un produit simple demande souvent plus de discipline qu’un produit riche en options.

---

## 3) Le design n’arrive pas “après” : il clarifie le produit

Sur Clarionet, les itérations visuelles (layout, hiérarchie, dialogues, branding) n’étaient pas décoratives.  
Elles ont révélé ce qui était confus dans le produit lui-même.

**Signal à surveiller :**
- si l’interface est difficile à organiser, c’est souvent le flux produit qui l’est aussi.

**Leçon :** travailler le design tôt aide à prendre de meilleures décisions fonctionnelles.

---

## 4) Le “renommage” et le branding sont des décisions produit

Harmoniser l’identité autour de Clarionet n’était pas cosmétique.  
C’était un moyen de rendre le projet cohérent et plus lisible.

**Pourquoi ça compte :**
- meilleure compréhension immédiate pour un nouvel utilisateur,
- meilleure cohérence entre app, docs, screenshots, site,
- moins d’ambiguïté pour la suite du projet.

**Leçon :** un nom clair et une identité stable réduisent la dette de communication.

---

## 5) Le travail invisible (docs, site, CI) est un multiplicateur

Le projet a pris une autre dimension quand j’ai ajouté :
- un site GitHub Pages (Jekyll),
- un pipeline GitHub Actions pour build/deploy,
- une doc de lancement simple.

**Impact réel :**
- onboarding plus rapide,
- moins de tâches manuelles,
- plus de confiance à chaque release.

**Leçon :** si tu veux qu’un projet vive, automatise tôt ce qui revient souvent.

---

## 6) Versionner souvent > attendre la “grosse release parfaite”

L’historique montre beaucoup d’itérations courtes : UI, métadonnées, pipeline, packaging, polish.  
Chaque petit incrément réduisait le risque du suivant.

**Pratique utile :**
- commits petits et explicites,
- release notes légères mais régulières,
- capture des changements visibles (screenshots/changelog).

**Leçon :** livrer en continu maintient l’élan et améliore la qualité des décisions.

---

## 7) Les raccourcis clavier et la persistance ne sont pas des extras

Sur une app utilitaire, ces détails font la différence :
- raccourcis cohérents,
- volume et station mémorisés,
- comportement prévisible au redémarrage.

**Leçon :** l’expérience perçue vient souvent de détails “non marketing” mais très concrets.

---

## 8) Savoir arrêter le polish est une compétence produit

J’ai passé du temps sur des retouches fines. Certaines étaient utiles, d’autres moins.  
La bonne question est devenue : “Est-ce que ça améliore un usage mesurable ?”

**Règle pratique :**
- si un polish n’améliore ni lisibilité, ni vitesse, ni fiabilité, il peut attendre.

**Leçon :** le bon timing, c’est de livrer quand la valeur utilisateur est claire, pas quand tout semble “parfait”.

---

## 9) La constance gagne toujours

Ce projet n’a pas avancé grâce à un sprint héroïque.  
Il a avancé grâce à des sessions régulières, avec des objectifs concrets.

**Leçon :** en side-project, la régularité est l’avantage compétitif principal.

---

## En résumé (actionnable)

Si tu développes une app similaire, je te recommande :
1. définir un usage central unique et livrer un MVP en premier,  
2. documenter + automatiser dès que possible,  
3. itérer en petits pas visibles,  
4. traiter design/UX comme des outils de clarification,  
5. protéger la simplicité comme une contrainte de produit.

Clarionet est aujourd’hui en version `87.5.025`, mais la vraie progression est surtout méthodologique : mieux décider, livrer plus proprement, et garder le cap sur l’essentiel.
