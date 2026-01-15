# Comment j'ai vibe-codé Clarionet, une app pour écouter des streams audio. 

13 janvier 2026, 9 h 24. Je trouve quelque chose à redire à la façon dont fonctionnent la [ribambelle](https://github.com/tuner-labs/tuner) d'apps que [j'utilise](https://goodvibes.readthedocs.io/en/stable/) pour [écouter des flux radio](https://apps.gnome.org/fr/Shortwave/). Tu vas rire, je ne me souviens même pas que quoi exactement. Toujours est-il que...

"Et si je vibe-codais, une app qui répond parfaitement à mes besoins pour cette fonction" me traverse les neurones. Je lance mon nouvel ami [opencode](https://opencode.ai/) et... hop !

14 janvier 2026, 11 h 14. Pendant que je suis en train de rédiger cette note, je suis en train d'écouter un fond sonore velouté à souhait via Clarionet, une app qui n'existait pas il y a trois jours. Parallèlement, je continue à peaufiner l'interface qui commence tout doucement à ressembler à quelque chose.

Clarionet est né d’une envie simple : écouter des radios en ligne sans lourdeur, sans compte, sans dépendances cloud. J'ai voulu un lecteur minimaliste, rapide et prévisible, qui s’efface derrière l’usage.

Oui, le nom Clarionet est un clin d'oeil non subtil dans la direction de Radio Cité. L'aspect de l'interface graphique lorgne - et ça n'est pas un hasard - en direction des récepteurs radios des années 80.

## Vibe coding

Avec opencode et un compte ChatGPT payant, nous avons créé cette petite app. Qu'est-ce que ça aurait donné avec un autre fournisseur et modèle (gpt-5.2 codex) ? Aucune idée. Est-ce que ça aurait été plus vite, plus facilement ? Aucune idée. Est-ce que je vais tester le même projet avec un autre modèle du même fournisseur et d'un autre ? Pas forcément.

Je n'ai *actuellement* aucune compétence en Python, ni en Rust. Mais, je parviens à parler le IA, à expliquer ce que je veux et comment corriger le tir quand l'outil hallucine.  

# I would like to thank the Academy and...

Sans le lecteur de flux pour terminal mpv et sans la base de données de radio-browser.info, ce projet aurait été impossible ou nettement plus velu à mettre en place. Merci-bisous à tous les contributeurs de ces deux projets.

## Intention

Le projet suit une ligne claire : pas de forme sans fonction, pas d’accumulation. Une seule fenêtre, des actions évidentes, des données locales et lisibles. Le but est de rendre l’écoute aussi immédiate que l’allumage d’un vieux poste, de préférence un poste influencé par le Bauhaus. Est-ce que j'ai un penchant pour le Bauhaus ? (la réponse est dans la question)

## Choix techniques

Je savais que je voulais utiliser mpv et le doter d'une interface graphique. Les deux autres choix techniques ont été effectués sur base de suggestion IA.

- **Python 3** pour la rapidité d’itération et la clarté du code.
- **GTK3 + PyGObject** pour une interface native sur Linux.
- **mpv** pour la lecture audio, via son socket IPC JSON.

Ces choix privilégient la robustesse et l’intégration système plutôt que l’effet “app web”.

## Architecture simple

J'ai donné à l'IA des consignes de robustesse et simplicité. Conséquence : le cœur tient dans un seul fichier : `clarionet.py`. Ceci rend l’application facile à parcourir et à modifier. Les données (radios, config, logs) vivent dans `~/.config/clarionet/` pour rester locales et transparentes. 

## Interface

Au fur et à mesure des itérations, j'ai senti en moi l'appel de l'autoradio comme métaphore visuelle. Je n'ai pas eu le réflexe de prendre un screenshot des nombreuses itérations. 

## Consommation

Session de mardi 13 janvier : 24% du quota - sesssion du mercredi 14 janvier : 33% du quota quotidien (et donnez-nous notre)

## Pareto

La loi des 80/20 s'applique à ce projet. J'ai très vite eu une app qui fonctionnait. (20%) J'ai employé le reste (80%) à peaufiner et simplifier l'interface utilisateur. 

## Ajouter des stations

Deux possibilités.

 1. tu effectues une recherche dans la base de données de [radio-browser.info"](https://www.radio-browser.info/)
 2. tu entres le nom et l'adresse du flux du stream audio de ton choix

## Interaction et états

L’application écoute les événements mpv (idle, loading, playing, paused) pour afficher l’état courant. Les raccourcis clavier suivent *actuellement* la logique d’un lecteur physique : espace pour lecture/pause, S pour stop, flèches pour le volume et la navigation. Je ne suis pas certain de garder le S pour Stop dans une prochaine itération.

## Design et ambiance

Au fur et à mesure du développement, j'ai vu l'interface évoluer vers un côté skin winamp puis vers la métaphore de l'autoradio. J'ai voulu éviter l'effet Sapin de Noël. Il n'y a aucune animation, juste une grille simple, une typographie lisible bien que LED, et un affichage “digital” pour le now‑playing. Le fond brossé et le vert LED rappellent l’univers des équipements audio cuvée années 80 sans tomber dans le rétro gratuit.

## Ce que Clarionet ne veut pas être

Big brother, va donc t'expliquer avec Papa et Maman. L'app pratique un respect forcené de la vie privée de l'utilisateur. Pas de comptes, pas de recommandations, pas de tracking. Clarionet reste un outil local, discret et stable. Cette contrainte est autant un choix éthique qu’une manière de garder l’application légère.

## Licence MIT

J'ai opté, sans beaucoup réfléchir, pour la licence MIT. Cette licence, née [tu ne devineras jamais où](https://web.mit.edu/) donne à toute personne recevant le logiciel (et ses fichiers) le droit illimité d'en user, le copier, le modifier, le fusionner, le publier, le distribuer, le vendre et le « sous-licencier » (l'incorporer dans une autre licence). La seule obligation est d'incorporer la notice de licence et de copyright dans toutes les copies. 




## Ce qui pourrait changer dans le futur


Je laisse ouverte la possibilité de passer de Python à Rust, parce que Rust.
- Meilleure accessibilité clavier
s- Packaging propre (desktop entry + icône)

