# Manage Stations Dialog — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remplacer les deux dialogs imbriqués ("Editer la liste" + "Ajouter une station") par un seul dialog unifié "Modifier les stations", ouvert directement au clic sur le bouton (sans menu intermédiaire).

**Architecture:** Le `Gtk.MenuButton` existant (`add_station_button`) est remplacé par un `Gtk.Button` simple. Son handler `_build_add_station_button` et la méthode `on_edit_station_list` sont supprimés. Une nouvelle méthode `on_manage_stations` construit et affiche le dialog unifié avec : (1) liste des stations enregistrées + suppression immédiate, (2) ajout manuel, (3) recherche Radio-Browser. Les suppressions s'appliquent immédiatement (comme `on_remove` existant). Le CSS existant est réutilisé et complété.

**Tech Stack:** Python 3, GTK 3 (PyGObject), CSS inline dans `_install_list_styles`

---

## Fichiers modifiés

- Modify: `clarionet.py` — toutes les modifications sont dans ce fichier unique

---

### Task 1 : Remplacer `_build_add_station_button` par un bouton simple

**Files:**
- Modify: `clarionet.py:1089-1106` (méthode `_build_add_station_button`)

Le `Gtk.MenuButton` avec son menu à un seul item est remplacé par un `Gtk.Button` direct.

- [ ] **Step 1 : Localiser la méthode à modifier**

Ligne 1089 de `clarionet.py` :
```python
def _build_add_station_button(self):
    menu = Gtk.Menu()

    add_stream_item = Gtk.MenuItem(label="Ajouter une station")

    add_stream_item.connect("activate", lambda *_: self.on_add(None))

    menu.append(add_stream_item)
    menu.show_all()

    button = Gtk.MenuButton()
    button.set_image(
        self.load_custom_icon("lucide-radio-tower.svg", "list-add-symbolic", 22)
    )
    button.set_popup(menu)
    button.get_style_context().add_class("preset-button")
    button.get_style_context().add_class("preset-add")
    return button
```

- [ ] **Step 2 : Remplacer par un bouton simple**

Remplacer entièrement la méthode par :
```python
def _build_add_station_button(self):
    button = Gtk.Button()
    button.set_image(
        self.load_custom_icon("lucide-radio-tower.svg", "list-add-symbolic", 22)
    )
    button.set_tooltip_text("Modifier les stations")
    button.connect("clicked", self.on_manage_stations)
    button.get_style_context().add_class("preset-button")
    button.get_style_context().add_class("preset-add")
    return button
```

- [ ] **Step 3 : Vérifier que le raccourci clavier Ctrl+N pointe vers la nouvelle méthode**

Chercher dans `clarionet.py` la ligne (~1284) :
```python
if control_pressed and event.keyval in (Gdk.KEY_n, Gdk.KEY_N):
    self.on_add(parent=self)
    return True
```
La remplacer par :
```python
if control_pressed and event.keyval in (Gdk.KEY_n, Gdk.KEY_N):
    self.on_manage_stations(None)
    return True
```

- [ ] **Step 4 : Lancer l'app pour vérifier que le bouton est visible et cliquable (sans crash)**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu : l'app se lance, le bouton antenne est visible, un clic ne fait rien (la méthode `on_manage_stations` n'existe pas encore — une `AttributeError` dans les logs est normale à ce stade).

- [ ] **Step 5 : Commit**

```bash
git add clarionet.py
git commit -m "refactor: replace MenuButton with simple Button for station management"
```

---

### Task 2 : Implémenter `on_manage_stations` — squelette du dialog

**Files:**
- Modify: `clarionet.py` — ajouter la méthode `on_manage_stations` après `on_add` (~ligne 2079)

- [ ] **Step 1 : Ajouter la méthode squelette après `on_add_browser`**

Localiser ligne ~2081 :
```python
def on_add_browser(self, *_, parent=None):
    self.on_add(parent=parent)
```

Ajouter juste après :
```python
def on_manage_stations(self, *_):
    dialog = Gtk.Dialog(title="Modifier les stations", parent=self, flags=0)
    dialog.get_style_context().add_class("app-window")
    close_button = dialog.add_button("Fermer", Gtk.ResponseType.CLOSE)
    close_button.get_style_context().add_class("edit-action-button")
    dialog.set_default_size(600, 620)

    content = dialog.get_content_area()
    content.set_spacing(12)
    content.set_margin_top(8)
    content.set_margin_bottom(8)
    content.set_margin_start(8)
    content.set_margin_end(8)
    content.get_style_context().add_class("edit-dialog")

    title_label = Gtk.Label(label="Modifier les stations", xalign=0)
    title_label.get_style_context().add_class("dialog-title")
    content.add(title_label)

    content.show_all()
    dialog.run()
    dialog.destroy()
```

- [ ] **Step 2 : Lancer l'app et vérifier que le clic ouvre le dialog vide**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu : clic sur le bouton antenne → dialog "Modifier les stations" s'ouvre avec titre et bouton Fermer fonctionnel.

- [ ] **Step 3 : Commit**

```bash
git add clarionet.py
git commit -m "feat: add on_manage_stations dialog skeleton"
```

---

### Task 3 : Section liste des stations avec suppression immédiate

**Files:**
- Modify: `clarionet.py` — compléter `on_manage_stations`

La liste affiche chaque station avec son nom (non éditable ici) et un bouton poubelle. La suppression est immédiate (pas de "Enregistrer") : elle appelle `on_remove_by_id` qui est la logique extraite de `on_remove`.

- [ ] **Step 1 : Ajouter la méthode helper `remove_radio_by_id`**

Cette méthode manquait dans le code (appelée dans `on_edit_station_list` mais jamais définie — bug existant). L'ajouter juste avant `on_manage_stations` :

```python
def remove_radio_by_id(self, radio_id):
    """Supprime une station par son ID : arrête la lecture si nécessaire,
    met à jour self.radios, self.listbox, config et sauvegarde."""
    if radio_id == self.playing_id:
        self.on_stop(None)
        self.playing_id = None
        self.playing_name = None
    row_to_remove = next(
        (r for r in self.listbox.get_children() if r.radio_id == radio_id),
        None,
    )
    if row_to_remove:
        self.listbox.remove(row_to_remove)
    self.radios = [r for r in self.radios if r["id"] != radio_id]
    if self.config.get("last_radio_id") == radio_id:
        self.config["last_radio_id"] = None
        save_json(CONFIG_PATH, self.config)
    save_json(RADIOS_PATH, self.radios)
    self.refresh_row_styles()
    self.refresh_preset_labels()
```

- [ ] **Step 2 : Réécrire `on_remove` pour utiliser `remove_radio_by_id`**

Remplacer `on_remove` (lignes 2083-2098) par :
```python
def on_remove(self, _):
    row = self.listbox.get_selected_row()
    if not row:
        return
    self.remove_radio_by_id(row.radio_id)
    self.current_label.set_text("-")
```

- [ ] **Step 3 : Ajouter la section liste dans `on_manage_stations`**

Dans `on_manage_stations`, juste avant `content.show_all()`, ajouter :

```python
    stations_label = Gtk.Label(label="Stations enregistrées", xalign=0)
    stations_label.get_style_context().add_class("dialog-section-label")
    content.add(stations_label)

    manage_list = Gtk.ListBox()
    manage_list.set_selection_mode(Gtk.SelectionMode.NONE)
    manage_list.get_style_context().add_class("edit-list")
    scrolled_stations = Gtk.ScrolledWindow()
    scrolled_stations.set_min_content_height(200)
    scrolled_stations.set_vexpand(False)
    scrolled_stations.get_style_context().add_class("edit-scrolled")
    scrolled_stations.add(manage_list)
    content.add(scrolled_stations)

    def build_station_rows():
        for child in manage_list.get_children():
            manage_list.remove(child)
        sorted_radios = sorted(self.radios, key=lambda r: r["name"].lower())
        for radio in sorted_radios:
            row = Gtk.ListBoxRow()
            row.radio_id = radio["id"]

            name_label = Gtk.Label(label=radio["name"], xalign=0)
            name_label.set_ellipsize(Pango.EllipsizeMode.END)
            name_label.set_hexpand(True)
            name_label.get_style_context().add_class("manage-station-name")

            url_label = Gtk.Label(label=radio.get("stream_url", ""), xalign=0)
            url_label.set_ellipsize(Pango.EllipsizeMode.END)
            url_label.set_hexpand(True)
            url_label.get_style_context().add_class("edit-url")

            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            info_box.set_hexpand(True)
            info_box.pack_start(name_label, False, False, 0)
            info_box.pack_start(url_label, False, False, 0)

            delete_button = Gtk.Button()
            delete_button.set_image(
                Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
            )
            delete_button.set_relief(Gtk.ReliefStyle.NONE)
            delete_button.set_tooltip_text("Supprimer")
            delete_button.get_style_context().add_class("edit-delete-button")

            def on_delete(btn, rid=radio["id"], lrow=row):
                self.remove_radio_by_id(rid)
                manage_list.remove(lrow)

            delete_button.connect("clicked", on_delete)

            row_box = Gtk.Box(spacing=8)
            row_box.set_margin_start(8)
            row_box.set_margin_end(8)
            row_box.set_margin_top(6)
            row_box.set_margin_bottom(6)
            row_box.get_style_context().add_class("edit-row")
            row_box.pack_start(info_box, True, True, 0)
            row_box.pack_start(delete_button, False, False, 0)
            row.add(row_box)
            manage_list.add(row)
        manage_list.show_all()

    build_station_rows()
```

- [ ] **Step 4 : Lancer l'app et vérifier la liste + suppression**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu :
- Le dialog affiche la liste des stations triées alphabétiquement
- Clic poubelle → la station disparaît immédiatement de la liste ET de la liste principale de l'app
- Si la station supprimée est en cours de lecture, la lecture s'arrête

- [ ] **Step 5 : Commit**

```bash
git add clarionet.py
git commit -m "feat: add station list with immediate deletion to manage stations dialog"
```

---

### Task 4 : Section ajout manuel dans le dialog unifié

**Files:**
- Modify: `clarionet.py` — compléter `on_manage_stations`

- [ ] **Step 1 : Ajouter le séparateur et la section saisie manuelle**

Dans `on_manage_stations`, après `build_station_rows()` et avant `content.show_all()`, ajouter :

```python
    sep1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    content.add(sep1)

    manual_label = Gtk.Label(label="Ajouter manuellement", xalign=0)
    manual_label.get_style_context().add_class("dialog-section-label")
    content.add(manual_label)

    manual_box = Gtk.Box(spacing=8)
    name_entry = Gtk.Entry()
    name_entry.set_placeholder_text("Nom")
    name_entry.set_hexpand(True)
    name_entry.get_style_context().add_class("add-entry")
    url_entry = Gtk.Entry()
    url_entry.set_placeholder_text("URL du stream")
    url_entry.set_hexpand(True)
    url_entry.get_style_context().add_class("add-entry")
    add_manual_button = Gtk.Button(label="Ajouter")
    add_manual_button.get_style_context().add_class("browser-button")
    manual_box.pack_start(name_entry, True, True, 0)
    manual_box.pack_start(url_entry, True, True, 0)
    manual_box.pack_start(add_manual_button, False, False, 0)
    content.add(manual_box)

    manual_status = Gtk.Label(label="", xalign=0)
    manual_status.get_style_context().add_class("browser-status")
    content.add(manual_status)

    def on_add_manual(_):
        name = name_entry.get_text().strip()
        url = url_entry.get_text().strip()
        if not name or not url:
            manual_status.set_text("Nom et URL requis.")
            return
        self.add_radios([{"name": name, "stream_url": url}])
        name_entry.set_text("")
        url_entry.set_text("")
        manual_status.set_text(f"« {name} » ajoutée.")
        build_station_rows()

    add_manual_button.connect("clicked", on_add_manual)
    name_entry.connect("activate", on_add_manual)
    url_entry.connect("activate", on_add_manual)
```

- [ ] **Step 2 : Lancer l'app et vérifier l'ajout manuel**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu :
- Saisir un nom + URL → clic "Ajouter" ou Entrée → la station apparaît immédiatement dans la liste du dialog ET dans la liste principale
- Message de confirmation affiché
- Champs vidés après ajout
- Si nom ou URL manquant : message d'erreur, aucune action

- [ ] **Step 3 : Commit**

```bash
git add clarionet.py
git commit -m "feat: add manual station entry to manage stations dialog"
```

---

### Task 5 : Section recherche Radio-Browser dans le dialog unifié

**Files:**
- Modify: `clarionet.py` — compléter `on_manage_stations`

- [ ] **Step 1 : Ajouter le séparateur et la section Radio-Browser**

Dans `on_manage_stations`, après le bloc ajout manuel et avant `content.show_all()`, ajouter :

```python
    sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    content.add(sep2)

    browser_label = Gtk.Label(label="Recherche Radio-Browser", xalign=0)
    browser_label.get_style_context().add_class("dialog-section-label")
    content.add(browser_label)

    search_box = Gtk.Box(spacing=8)
    search_box.get_style_context().add_class("browser-search")
    search_entry = Gtk.Entry()
    search_entry.set_placeholder_text("Recherche par nom")
    search_entry.set_hexpand(True)
    search_entry.get_style_context().add_class("browser-entry")
    search_button = Gtk.Button(label="Rechercher")
    search_button.get_style_context().add_class("browser-button")
    search_box.pack_start(search_entry, True, True, 0)
    search_box.pack_start(search_button, False, False, 0)
    content.add(search_box)

    browser_status = Gtk.Label(label="", xalign=0)
    browser_status.get_style_context().add_class("browser-status")
    content.add(browser_status)

    results_list = Gtk.ListBox()
    results_list.set_selection_mode(Gtk.SelectionMode.NONE)
    results_list.get_style_context().add_class("browser-list")
    scrolled_results = Gtk.ScrolledWindow()
    scrolled_results.set_vexpand(True)
    scrolled_results.set_min_content_height(160)
    scrolled_results.get_style_context().add_class("browser-scrolled")
    scrolled_results.add(results_list)
    content.add(scrolled_results)

    add_selected_button = Gtk.Button(label="Ajouter la sélection")
    add_selected_button.get_style_context().add_class("browser-button")
    add_selected_button.set_halign(Gtk.Align.END)
    add_selected_button.set_sensitive(False)
    content.add(add_selected_button)

    def clear_results():
        for child in results_list.get_children():
            results_list.remove(child)

    def populate_results(stations, warning=None):
        clear_results()
        count = 0
        for station in stations:
            name = station.get("name", "").strip()
            url = station.get("url_resolved") or station.get("url")
            if not name or not url:
                continue
            country = station.get("country", "").strip()
            codec = station.get("codec", "").strip()
            bitrate = station.get("bitrate")
            details = []
            if codec:
                details.append(codec.upper())
            if bitrate:
                details.append(f"{bitrate} kbps")
            if station.get("hls"):
                details.append("HLS")
            base_label = f"{name} ({country})" if country else name
            label_text = (
                f"{base_label} — {' · '.join(details)}" if details else base_label
            )
            check = Gtk.CheckButton(label=label_text)
            check.get_style_context().add_class("browser-check")
            check.set_margin_start(8)
            check.set_margin_end(8)
            check.set_margin_top(6)
            check.set_margin_bottom(6)
            check.connect("toggled", lambda *_: add_selected_button.set_sensitive(
                any(
                    r.get_child().get_active()
                    for r in results_list.get_children()
                )
            ))
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("browser-result")
            row.station = {
                "name": name,
                "stream_url": url,
                "homepage": station.get("homepage"),
                "favicon": station.get("favicon"),
            }
            row.add(check)
            results_list.add(row)
            count += 1
            if count >= 25:
                break
        results_list.show_all()
        status_text = f"{count} résultat(s)"
        if warning:
            status_text += f" — {warning}"
        browser_status.set_text(status_text)
        search_button.set_sensitive(True)

    def on_result(stations, warning=None):
        populate_results(stations, warning)
        return False

    def on_error(message):
        browser_status.set_text(f"Erreur : {message}")
        search_button.set_sensitive(True)
        return False

    def on_search_clicked(_):
        query = search_entry.get_text().strip()
        if not query:
            browser_status.set_text("Saisir un nom de station.")
            return
        browser_status.set_text("Recherche en cours…")
        search_button.set_sensitive(False)
        add_selected_button.set_sensitive(False)
        self.fetch_radio_browser(query, on_result, on_error)

    def on_add_selected(_):
        selected = [
            row.station
            for row in results_list.get_children()
            if row.get_child().get_active()
        ]
        if not selected:
            return
        self.add_radios(selected)
        clear_results()
        browser_status.set_text(f"{len(selected)} station(s) ajoutée(s).")
        add_selected_button.set_sensitive(False)
        build_station_rows()

    search_button.connect("clicked", on_search_clicked)
    search_entry.connect("activate", on_search_clicked)
    add_selected_button.connect("clicked", on_add_selected)
```

- [ ] **Step 2 : Lancer l'app et tester la recherche Radio-Browser**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu :
- Saisir "FIP" → Rechercher → liste de résultats s'affiche avec cases à cocher
- Cocher plusieurs stations → bouton "Ajouter la sélection" s'active
- Clic "Ajouter la sélection" → stations ajoutées, liste du dialog rafraîchie, résultats effacés
- Le bouton "Ajouter la sélection" reste grisé si rien n'est coché

- [ ] **Step 3 : Commit**

```bash
git add clarionet.py
git commit -m "feat: add Radio-Browser search to manage stations dialog"
```

---

### Task 6 : CSS — styles de la section label et nettoyage

**Files:**
- Modify: `clarionet.py` — méthode `_install_list_styles` (~ligne 2280)

- [ ] **Step 1 : Ajouter la règle CSS `.dialog-section-label`**

Dans le bloc CSS de `_install_list_styles`, dans la section des styles dialog (après `.edit-dialog .edit-url`), ajouter :

```css
        .dialog-section-label {{
            font-weight: 600;
            font-size: 13px;
            color: #b3b3b3;
            margin-top: 4px;
        }}
        .manage-station-name {{
            font-size: 14px;
            color: #f2f2f2;
        }}
```

Trouver le bloc à modifier : c'est la chaîne `css = f"""` dans `_install_list_styles`. Ajouter ces règles après `.edit-dialog .edit-url` (ligne ~2471).

- [ ] **Step 2 : Vérifier le rendu visuel**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu : les labels de section ("Stations enregistrées", "Ajouter manuellement", "Recherche Radio-Browser") s'affichent en gris clair, légèrement plus petits que le titre principal.

- [ ] **Step 3 : Commit**

```bash
git add clarionet.py
git commit -m "style: add CSS rules for manage stations dialog sections"
```

---

### Task 7 : Supprimer le code obsolète

**Files:**
- Modify: `clarionet.py` — supprimer `on_edit_station_list` et `on_add_browser`

- [ ] **Step 1 : Vérifier qu'`on_edit_station_list` n'est plus appelée nulle part**

```bash
grep -n "on_edit_station_list\|on_add_browser\|on_add(" /home/Baudouin/Documents/Projets/radiocity/clarionet.py
```
Attendu : `on_edit_station_list` n'apparaît qu'à sa définition. `on_add_browser` n'apparaît qu'à sa définition. `on_add(` n'apparaît plus dans aucun handler (uniquement sa définition).

- [ ] **Step 2 : Supprimer `on_edit_station_list` (lignes 1731-1900)**

Supprimer entièrement la méthode `on_edit_station_list` du fichier.

- [ ] **Step 3 : Supprimer `on_add_browser` (~ligne 2080-2081)**

Supprimer entièrement :
```python
def on_add_browser(self, *_, parent=None):
    self.on_add(parent=parent)
```

- [ ] **Step 4 : Vérifier que l'app fonctionne toujours**

```bash
cd /home/Baudouin/Documents/Projets/radiocity && python3 clarionet.py
```
Attendu : aucun crash, le dialog "Modifier les stations" fonctionne normalement.

- [ ] **Step 5 : Commit**

```bash
git add clarionet.py
git commit -m "refactor: remove obsolete on_edit_station_list and on_add_browser methods"
```

---

## Self-Review — Couverture du design

| Exigence design | Task couvrant |
|---|---|
| Clic direct sur icône → ouvre le dialog | Task 1 |
| Dialog unique (plus de menu) | Task 1 |
| Liste des stations enregistrées visible | Task 3 |
| Suppression immédiate avec mise à jour UI | Task 3 + `remove_radio_by_id` |
| Ajout manuel (nom + URL) | Task 4 |
| Recherche Radio-Browser avec cases à cocher | Task 5 |
| Bouton "Ajouter la sélection" conditionnel | Task 5 |
| Styles cohérents avec l'app | Task 6 |
| Code obsolète supprimé | Task 7 |
| Bug `remove_radio_by_id` manquant corrigé | Task 3 |
| Ctrl+N redirigé | Task 1 |
