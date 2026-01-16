---
layout: page
lede_fr: "Une interface rapide et locale, inspirée des autoradios des années 80, pensée pour écouter sans distraction."
lede_en: "A fast and local interface inspired by 80s car radios, designed for distraction-free listening."
---

<div class="hero">
  <div class="badge">
    <span class="badge-icon">📻</span>
    <span>{{ site.version }}</span>
  </div>
  <h1>Clarionet</h1>
  <p class="lede fr">{{ page.lede_fr }}</p>
  <p class="lede en">{{ page.lede_en }}</p>
  <div class="hero-actions">
    <a href="#install" class="btn btn-primary"><span class="fr">Installer</span><span class="en">Install</span></a>
    <a href="https://github.com/{{ site.github_username }}/{{ site.github_repo }}" class="btn btn-secondary">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
      </svg>
      GitHub
    </a>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="preview">
      <img src="{{ '/assets/screenshots/clarionet-main.png' | prepend: site.baseurl }}" alt="Clarionet interface" loading="lazy" />
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <h2 class="section-title fr">Fonctionnalités</h2>
    <h2 class="section-title en">Features</h2>
    {% include features.html %}
  </div>
</section>

<section class="section" id="install">
  <div class="container">
    <h2 class="section-title fr">Installation</h2>
    <h2 class="section-title en">Installation</h2>

    <div class="install-methods">
      <div class="install-card active">
        <div class="install-header">
          <h3 class="fr">Local (recommandé)</h3>
          <h3 class="en">Local (recommended)</h3>
          <span class="install-badge">Simple</span>
        </div>
        <div class="install-body">
          <pre><code>git clone https://github.com/{{ site.github_username }}/{{ site.github_repo }}.git
cd Clarionet
./install.sh</code></pre>
          <p class="install-note fr">Lancement : <code>./clarionet</code></p>
          <p class="install-note en">Launch : <code>./clarionet</code></p>
        </div>
      </div>

      <div class="install-card">
        <div class="install-header">
          <h3>DEB (Debian/Ubuntu)</h3>
          <span class="install-badge">.deb</span>
        </div>
        <div class="install-body">
          <pre><code>wget https://github.com/{{ site.github_username }}/{{ site.github_repo }}/releases/download/v{{ site.version }}/clarionet_{{ site.version }}_amd64.deb
sudo dpkg -i clarionet_{{ site.version }}_amd64.deb</code></pre>
        </div>
      </div>

      <div class="install-card">
        <div class="install-header">
          <h3>RPM (Fedora/RHEL)</h3>
          <span class="install-badge">.rpm</span>
        </div>
        <div class="install-body">
          <pre><code>wget https://github.com/{{ site.github_username }}/{{ site.github_repo }}/releases/download/v{{ site.version }}/clarionet-{{ site.version }}-1.x86_64.rpm
sudo dnf install clarionet-{{ site.version }}-1.x86_64.rpm</code></pre>
        </div>
      </div>

      <div class="install-card">
        <div class="install-header">
          <h3>Arch Linux (AUR)</h3>
          <span class="install-badge">AUR</span>
        </div>
        <div class="install-body">
          <pre><code>yay -S clarionet-git
# ou
paru -S clarionet-git</code></pre>
        </div>
      </div>
    </div>

    <div class="dependencies">
      <h4 class="fr">Dépendances</h4>
      <h4 class="en">Dependencies</h4>
      <ul>
        <li>Python 3</li>
        <li>GTK3 + PyGObject</li>
        <li>mpv</li>
      </ul>
    </div>
  </div>
</section>

<section class="section section-alt" id="shortcuts">
  <div class="container">
    <h2 class="section-title fr">Raccourcis clavier</h2>
    <h2 class="section-title en">Keyboard shortcuts</h2>

    <div class="shortcuts-table">
      <table>
        <thead>
          <tr>
            <th class="fr">Touche</th>
            <th class="en">Key</th>
            <th class="fr">Action</th>
            <th class="en">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><kbd>Space</kbd></td>
            <td class="fr">Lecture / Pause</td>
            <td class="en">Play / Pause</td>
          </tr>
          <tr>
            <td><kbd>S</kbd></td>
            <td class="fr">Arrêt</td>
            <td class="en">Stop</td>
          </tr>
          <tr>
            <td><kbd>←</kbd> / <kbd>→</kbd></td>
            <td class="fr">Volume − / +</td>
            <td class="en">Volume − / +</td>
          </tr>
          <tr>
            <td><kbd>↑</kbd> / <kbd>↓</kbd></td>
            <td class="fr">Station précédente / suivante</td>
            <td class="en">Previous / Next station</td>
          </tr>
          <tr>
            <td><kbd>Ctrl</kbd> + <kbd>N</kbd></td>
            <td class="fr">Ajouter une radio</td>
            <td class="en">Add a radio</td>
          </tr>
          <tr>
            <td><kbd>Ctrl</kbd> + <kbd>Q</kbd></td>
            <td class="fr">Quitter</td>
            <td class="en">Quit</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="section" id="philosophy">
  <div class="container">
    <h2 class="section-title fr">Philosophie</h2>
    <h2 class="section-title en">Philosophy</h2>

    <div class="philosophy-content">
      <div class="philosophy-text">
        <p class="fr">
          Clarionet privilégie la sobriété : peu d'éléments visibles, des actions directes,
          et une interface inspirée des autoradios des années 80.
          Les données restent locales dans <code>~/.config/clarionet/</code>.
          Pas de compte utilisateur, pas de cloud, pas de tracking.
        </p>
        <p class="en">
          Clarionet prioritizes simplicity: fewer visible elements, direct actions,
          and an interface inspired by 80s car radios.
          Data stays local in <code>~/.config/clarionet/</code>.
          No user accounts, no cloud, no tracking.
        </p>
      </div>

      <div class="philosophy-values">
        <div class="value-item">
          <div class="value-icon">🎯</div>
          <h4 class="fr">Fonction avant forme</h4>
          <h4 class="en">Function over form</h4>
        </div>
        <div class="value-item">
          <div class="value-icon">📦</div>
          <h4 class="fr">Pas de dépendances inutiles</h4>
          <h4 class="en">No unnecessary dependencies</h4>
        </div>
        <div class="value-item">
          <div class="value-icon">🔐</div>
          <h4 class="fr">Protection de la vie privée</h4>
          <h4 class="en">Privacy first</h4>
        </div>
        <div class="value-item">
          <div class="value-icon">⚙️</div>
          <h4 class="fr">Intégration Linux native</h4>
          <h4 class="en">Native Linux integration</h4>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt" id="download">
  <div class="container">
    <h2 class="section-title fr">Télécharger</h2>
    <h2 class="section-title en">Download</h2>

    <div class="download-section">
      <a href="https://github.com/{{ site.github_username }}/{{ site.github_repo }}/releases/latest" class="download-btn">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
        </svg>
        <span class="fr">Télécharger v{{ site.version }}</span>
        <span class="en">Download v{{ site.version }}</span>
      </a>

      <div class="download-links">
        <a href="https://github.com/{{ site.github_username }}/{{ site.github_repo }}/releases/latest">
          DEB / RPM / Arch
        </a>
        <a href="https://github.com/{{ site.github_username }}/{{ site.github_repo }}">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          Source Code
        </a>
        <a href="https://github.com/{{ site.github_username }}/{{ site.github_repo }}/issues">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0012 2z"/>
          </svg>
          Report Issue
        </a>
      </div>
    </div>
  </div>
</section>

<section class="section" id="contribute">
  <div class="container">
    <h2 class="section-title fr">Contribuer</h2>
    <h2 class="section-title en">Contribute</h2>

    <div class="contribute-content">
      <p class="fr">
        Clarionet est un projet open source. Les contributions sont les bienvenues !
        Signalez des bugs, proposez des fonctionnalités, ou envoyez des pull requests.
      </p>
      <p class="en">
        Clarionet is an open source project. Contributions are welcome!
        Report bugs, suggest features, or send pull requests.
      </p>
    </div>
  </div>
</section>
