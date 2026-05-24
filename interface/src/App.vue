<script setup>
import { computed, onMounted, ref } from 'vue'

const adresseServeur = 'http://127.0.0.1:8787'

const langueInterface = ref('fr')
const langue = ref('auto')
const modele = ref('tiny')
const styleSelectionne = ref('imperial')

const etatServeur = ref('verification')
const infosServeur = ref(null)
const fichierSelectionne = ref(null)
const resultatTeleversement = ref(null)
const resultatTache = ref(null)
const resultatExecution = ref(null)
const forgeEnCours = ref(false)
const erreurInterface = ref('')
const journal = ref('Forge Souveraine attend un fichier.')

const textes = {
  fr: {
    app: 'Forge Souveraine',
    sousTitre: 'Atelier local de sous-titres imperiaux',
    statut: 'Statut',
    apiOk: 'API en ligne',
    apiNon: 'API indisponible',
    langueInterface: 'Interface',
    francais: 'Français',
    russe: 'Русский',
    fichier: 'Fichier',
    choisir: 'Choisir une video ou un audio',
    deposer: 'Selectionne un MP4, MOV, WEBM, MP3, WAV ou M4A.',
    fichierChoisi: 'Fichier choisi',
    aucunFichier: 'Aucun fichier choisi',
    reglages: 'Reglages',
    langueAudio: 'Langue audio',
    auto: 'Auto',
    ru: 'Russe',
    fr: 'Français',
    en: 'Anglais',
    modele: 'Modele Whisper',
    rapide: 'rapide',
    equilibre: 'equilibre',
    plusPrecis: 'plus precis',
    style: 'Style',
    imperial: 'Imperial',
    forger: 'Forger les sous-titres',
    enCours: 'Forge en cours...',
    pipeline: 'Pipeline',
    journal: 'Journal',
    resultats: 'Resultats',
    pret: 'Pret',
    attente: 'Attente',
    actif: 'En cours',
    fait: 'Fait',
    erreur: 'Erreur',
    televersement: 'Upload local',
    tache: 'Tache',
    transcription: 'Transcription',
    rendu: 'Rendu MP4',
    sorties: 'Sorties',
    telechargerSrt: 'Telecharger SRT',
    telechargerAss: 'Telecharger ASS',
    telechargerJson: 'Telecharger JSON',
    telechargerMp4: 'Telecharger MP4',
    ouvrirServeur: 'Verifier le serveur',
    noteLocale: 'Tout reste local sur cette machine.',
    videoOnly: 'Le MP4 est genere seulement pour une entree video.',
    erreurFichier: 'Choisis d abord un fichier.',
    sauvegarde: 'Fichier sauvegarde. Creation de la tache...',
    tacheCreee: 'Tache creee. Transcription en cours...',
    premierLancement: 'Le premier lancement peut telecharger le modele Whisper.',
    renduEnCours: 'Transcription terminee. Rendu video en cours...',
    transcriptionTerminee: 'Transcription terminee.',
    termineAvecProbleme: 'La tache est terminee avec probleme.',
    pretATravailler: 'Pret a travailler',
    ouvrirResultats: 'Les sorties seront disponibles ici apres la forge.'
  },
  ru: {
    app: 'Forge Souveraine',
    sousTitre: 'Локальная кузница имперских субтитров',
    statut: 'Статус',
    apiOk: 'API онлайн',
    apiNon: 'API недоступен',
    langueInterface: 'Интерфейс',
    francais: 'Français',
    russe: 'Русский',
    fichier: 'Файл',
    choisir: 'Выбрать видео или аудио',
    deposer: 'Выбери MP4, MOV, WEBM, MP3, WAV или M4A.',
    fichierChoisi: 'Файл выбран',
    aucunFichier: 'Файл не выбран',
    reglages: 'Настройки',
    langueAudio: 'Язык аудио',
    auto: 'Авто',
    ru: 'Русский',
    fr: 'Французский',
    en: 'Английский',
    modele: 'Модель Whisper',
    rapide: 'быстро',
    equilibre: 'баланс',
    plusPrecis: 'точнее',
    style: 'Стиль',
    imperial: 'Имперский',
    forger: 'Создать субтитры',
    enCours: 'Кузница работает...',
    pipeline: 'Процесс',
    journal: 'Журнал',
    resultats: 'Результаты',
    pret: 'Готово',
    attente: 'Ожидание',
    actif: 'В процессе',
    fait: 'Готово',
    erreur: 'Ошибка',
    televersement: 'Локальная загрузка',
    tache: 'Задача',
    transcription: 'Транскрибация',
    rendu: 'Рендер MP4',
    sorties: 'Файлы',
    telechargerSrt: 'Скачать SRT',
    telechargerAss: 'Скачать ASS',
    telechargerJson: 'Скачать JSON',
    telechargerMp4: 'Скачать MP4',
    ouvrirServeur: 'Проверить сервер',
    noteLocale: 'Всё остаётся локально на этой машине.',
    videoOnly: 'MP4 создаётся только если на входе видео.',
    erreurFichier: 'Сначала выбери файл.',
    sauvegarde: 'Файл сохранён. Создаю задачу...',
    tacheCreee: 'Задача создана. Идёт транскрибация...',
    premierLancement: 'Первый запуск может скачать модель Whisper.',
    renduEnCours: 'Транскрибация готова. Идёт рендер видео...',
    transcriptionTerminee: 'Транскрибация завершена.',
    termineAvecProbleme: 'Задача завершилась с проблемой.',
    pretATravailler: 'Можно работать',
    ouvrirResultats: 'После кузницы результаты появятся здесь.'
  }
}

const t = (cle) => textes[langueInterface.value]?.[cle] ?? textes.fr[cle] ?? cle

const etapes = computed(() => [
  { code: 'televersement', titre: t('televersement') },
  { code: 'tache', titre: t('tache') },
  { code: 'transcription', titre: t('transcription') },
  { code: 'rendu', titre: t('rendu') },
  { code: 'sorties', titre: t('sorties') }
])

const nomFichier = computed(() => fichierSelectionne.value?.name || '')
const tailleFichier = computed(() => formatOctets(fichierSelectionne.value?.size || 0))
const estVideo = computed(() => entreeEstVideo(nomFichier.value))
const serveurPret = computed(() => etatServeur.value === 'pret')
const peutForger = computed(() => fichierSelectionne.value && !forgeEnCours.value && serveurPret.value)

function formatOctets(octets) {
  if (!octets) return '0 B'

  const unites = ['B', 'KB', 'MB', 'GB']
  let valeur = octets
  let index = 0

  while (valeur >= 1024 && index < unites.length - 1) {
    valeur = valeur / 1024
    index += 1
  }

  return valeur.toFixed(index === 0 ? 0 : 1) + ' ' + unites[index]
}

function entreeEstVideo(nom) {
  return /\.(mp4|mov|mkv|webm|m4v)$/i.test(nom || '')
}

function lienSortie(nomFichierSortie) {
  return adresseServeur + '/api/sorties/' + encodeURIComponent(nomFichierSortie)
}

function statutEtape(code) {
  if (resultatExecution.value?.etat === 'erreur' || resultatTache.value?.etat === 'erreur') {
    if (
      (code === 'transcription' && resultatTache.value?.etape === 'transcription_erreur') ||
      (code === 'rendu' && resultatTache.value?.etape === 'rendu_erreur')
    ) {
      return 'erreur'
    }
  }

  if (code === 'televersement') {
    if (resultatTeleversement.value) return 'fait'
    if (forgeEnCours.value) return 'actif'
    return 'attente'
  }

  if (code === 'tache') {
    if (resultatTache.value) return 'fait'
    if (resultatTeleversement.value && forgeEnCours.value) return 'actif'
    return 'attente'
  }

  if (code === 'transcription') {
    if (resultatExecution.value?.sorties?.srt) return 'fait'
    if (resultatTache.value?.etape === 'transcription') return 'actif'
    if (resultatTache.value) return 'attente'
    return 'attente'
  }

  if (code === 'rendu') {
    if (!estVideo.value) return 'attente'
    if (resultatExecution.value?.sorties?.mp4) return 'fait'
    if (resultatTache.value?.etape === 'rendu_video') return 'actif'
    return 'attente'
  }

  if (code === 'sorties') {
    if (resultatExecution.value?.sorties) return 'fait'
    return 'attente'
  }

  return 'attente'
}

function etiquetteStatut(statut) {
  if (statut === 'fait') return t('fait')
  if (statut === 'actif') return t('actif')
  if (statut === 'erreur') return t('erreur')
  return t('attente')
}

async function verifierServeur() {
  etatServeur.value = 'verification'

  try {
    const reponse = await fetch(adresseServeur + '/api/sante')

    if (!reponse.ok) {
      throw new Error('Backend HTTP ' + reponse.status)
    }

    infosServeur.value = await reponse.json()
    etatServeur.value = 'pret'
    journal.value = t('pretATravailler')
  } catch (erreur) {
    infosServeur.value = null
    etatServeur.value = 'erreur'
    journal.value = t('apiNon') + ': ' + erreur.message
  }
}

function choisirFichier(evenement) {
  const fichier = evenement.target.files?.[0] || null

  fichierSelectionne.value = fichier
  resultatTeleversement.value = null
  resultatTache.value = null
  resultatExecution.value = null
  erreurInterface.value = ''

  journal.value = fichier
    ? t('fichierChoisi') + ': ' + fichier.name + ' (' + formatOctets(fichier.size) + ')'
    : t('aucunFichier')
}

async function forgerSousTitres() {
  if (!fichierSelectionne.value) {
    erreurInterface.value = t('erreurFichier')
    return
  }

  forgeEnCours.value = true
  erreurInterface.value = ''
  resultatTeleversement.value = null
  resultatTache.value = null
  resultatExecution.value = null

  try {
    const formulaire = new FormData()
    formulaire.append('fichier', fichierSelectionne.value)

    journal.value = t('sauvegarde')

    const reponse = await fetch(adresseServeur + '/api/televerser', {
      method: 'POST',
      body: formulaire
    })

    if (!reponse.ok) {
      const texteErreur = await reponse.text()
      throw new Error(texteErreur)
    }

    const donnees = await reponse.json()
    resultatTeleversement.value = donnees

    journal.value = t('sauvegarde') + '\n' + donnees.nom_stocke

    const reponseTache = await fetch(adresseServeur + '/api/taches/creer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        nom_stocke: donnees.nom_stocke,
        langue: langue.value,
        modele: modele.value,
        style: styleSelectionne.value
      })
    })

    if (!reponseTache.ok) {
      const texteErreurTache = await reponseTache.text()
      throw new Error(texteErreurTache)
    }

    const tache = await reponseTache.json()
    resultatTache.value = tache

    journal.value =
      t('tacheCreee') + '\n' +
      'ID: ' + tache.identifiant_tache + '\n' +
      t('premierLancement')

    const reponseExecution = await fetch(
      adresseServeur + '/api/taches/' + tache.identifiant_tache + '/executer',
      { method: 'POST' }
    )

    if (!reponseExecution.ok) {
      const texteErreurExecution = await reponseExecution.text()
      throw new Error(texteErreurExecution)
    }

    let execution = await reponseExecution.json()
    resultatExecution.value = execution
    resultatTache.value = execution

    if (execution.etat === 'terminee' && entreeEstVideo(tache.nom_stocke)) {
      journal.value =
        t('renduEnCours') + '\n' +
        'ASS: ' + execution.sorties.ass

      const reponseRendu = await fetch(
        adresseServeur + '/api/taches/' + tache.identifiant_tache + '/rendre',
        { method: 'POST' }
      )

      if (!reponseRendu.ok) {
        const texteErreurRendu = await reponseRendu.text()
        throw new Error(texteErreurRendu)
      }

      execution = await reponseRendu.json()
      resultatExecution.value = execution
      resultatTache.value = execution
    }

    if (execution.etat === 'terminee') {
      journal.value =
        t('transcriptionTerminee') + '\n' +
        'Segments: ' + execution.segments + '\n' +
        'Langue: ' + execution.langue_detectee + '\n' +
        'SRT: ' + execution.sorties.srt + '\n' +
        'ASS: ' + execution.sorties.ass + '\n' +
        'JSON: ' + execution.sorties.json +
        (execution.sorties.mp4 ? '\nMP4: ' + execution.sorties.mp4 : '')
    } else {
      journal.value =
        t('termineAvecProbleme') + '\n' +
        'Etat: ' + execution.etat + '\n' +
        'Etape: ' + execution.etape + '\n' +
        'Erreur: ' + (execution.erreur || 'inconnue')
    }
  } catch (erreur) {
    erreurInterface.value = erreur.message
    journal.value = t('erreur') + ': ' + erreur.message
  } finally {
    forgeEnCours.value = false
  }
}

onMounted(() => {
  verifierServeur()
})
</script>

<template>
  <main class="coquille">
    <aside class="barre-laterale">
      <div class="marque">
        <div class="sceau">FS</div>
        <div>
          <h1>{{ t('app') }}</h1>
          <p>{{ t('sousTitre') }}</p>
        </div>
      </div>

      <section class="bloc">
        <div class="titre-ligne">
          <span>{{ t('statut') }}</span>
          <button class="bouton-mini" type="button" @click="verifierServeur">
            {{ t('ouvrirServeur') }}
          </button>
        </div>

        <div class="pastille" :class="etatServeur">
          <span class="point"></span>
          {{ serveurPret ? t('apiOk') : t('apiNon') }}
        </div>

        <p class="note">{{ t('noteLocale') }}</p>
      </section>

      <section class="bloc">
        <label>{{ t('langueInterface') }}</label>
        <div class="segmente">
          <button
            type="button"
            :class="{ actif: langueInterface === 'fr' }"
            @click="langueInterface = 'fr'"
          >
            {{ t('francais') }}
          </button>
          <button
            type="button"
            :class="{ actif: langueInterface === 'ru' }"
            @click="langueInterface = 'ru'"
          >
            {{ t('russe') }}
          </button>
        </div>
      </section>

      <section class="bloc">
        <h2>{{ t('reglages') }}</h2>

        <label for="langue-audio">{{ t('langueAudio') }}</label>
        <select id="langue-audio" v-model="langue">
          <option value="auto">{{ t('auto') }}</option>
          <option value="ru">{{ t('ru') }}</option>
          <option value="fr">{{ t('fr') }}</option>
          <option value="en">{{ t('en') }}</option>
        </select>

        <label for="modele">{{ t('modele') }}</label>
        <select id="modele" v-model="modele">
          <option value="tiny">tiny, {{ t('rapide') }}</option>
          <option value="base">base, {{ t('equilibre') }}</option>
          <option value="small">small, {{ t('plusPrecis') }}</option>
        </select>

        <label for="style">{{ t('style') }}</label>
        <select id="style" v-model="styleSelectionne">
          <option value="imperial">{{ t('imperial') }}</option>
        </select>

        <p class="note">{{ t('videoOnly') }}</p>
      </section>
    </aside>

    <section class="atelier">
      <header class="bandeau">
        <div>
          <p class="sur-titre">{{ t('pret') }}</p>
          <h2>{{ t('choisir') }}</h2>
        </div>
        <div class="badge-modele">{{ modele }}</div>
      </header>

      <label class="zone-fichier">
        <input type="file" accept=".mp4,.mov,.mkv,.webm,.m4v,.mp3,.wav,.m4a" @change="choisirFichier" />
        <span class="icone-upload">⬆</span>
        <strong>{{ fichierSelectionne ? t('fichierChoisi') : t('choisir') }}</strong>
        <em>{{ fichierSelectionne ? nomFichier : t('deposer') }}</em>
      </label>

      <div class="fiche-fichier">
        <div>
          <span>{{ t('fichier') }}</span>
          <strong>{{ fichierSelectionne ? nomFichier : t('aucunFichier') }}</strong>
        </div>
        <div>
          <span>Type</span>
          <strong>{{ estVideo ? 'Video' : 'Audio' }}</strong>
        </div>
        <div>
          <span>Size</span>
          <strong>{{ tailleFichier }}</strong>
        </div>
      </div>

      <button class="bouton-principal" type="button" :disabled="!peutForger" @click="forgerSousTitres">
        <span v-if="forgeEnCours">{{ t('enCours') }}</span>
        <span v-else>{{ t('forger') }}</span>
      </button>

      <p v-if="erreurInterface" class="alerte">{{ erreurInterface }}</p>
    </section>

    <aside class="panneau-droit">
      <section class="bloc haut">
        <h2>{{ t('pipeline') }}</h2>

        <div class="pipeline">
          <div v-for="etape in etapes" :key="etape.code" class="etape" :class="statutEtape(etape.code)">
            <span class="numero"></span>
            <div>
              <strong>{{ etape.titre }}</strong>
              <small>{{ etiquetteStatut(statutEtape(etape.code)) }}</small>
            </div>
          </div>
        </div>
      </section>

      <section class="bloc">
        <h2>{{ t('resultats') }}</h2>

        <div v-if="resultatExecution?.sorties" class="telechargements">
          <a :href="lienSortie(resultatExecution.sorties.srt)" target="_blank">{{ t('telechargerSrt') }}</a>
          <a :href="lienSortie(resultatExecution.sorties.ass)" target="_blank">{{ t('telechargerAss') }}</a>
          <a :href="lienSortie(resultatExecution.sorties.json)" target="_blank">{{ t('telechargerJson') }}</a>
          <a
            v-if="resultatExecution.sorties.mp4"
            :href="lienSortie(resultatExecution.sorties.mp4)"
            target="_blank"
          >
            {{ t('telechargerMp4') }}
          </a>
        </div>

        <p v-else class="note">{{ t('ouvrirResultats') }}</p>
      </section>

      <section class="bloc journal">
        <h2>{{ t('journal') }}</h2>
        <pre>{{ journal }}</pre>
      </section>
    </aside>
  </main>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 0%, rgba(214, 178, 24, 0.16), transparent 28%),
    radial-gradient(circle at 82% 10%, rgba(125, 255, 178, 0.12), transparent 24%),
    linear-gradient(135deg, #020604 0%, #07130b 48%, #020302 100%);
  color: #f5f0d4;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}

button,
select,
input {
  font: inherit;
}

.coquille {
  display: grid;
  grid-template-columns: 310px minmax(420px, 1fr) 380px;
  gap: 18px;
  width: 100vw;
  min-height: 100vh;
  padding: 18px;
}

.barre-laterale,
.atelier,
.panneau-droit {
  min-width: 0;
}

.barre-laterale,
.panneau-droit {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.marque,
.bloc,
.atelier {
  border: 1px solid rgba(214, 178, 24, 0.22);
  background:
    linear-gradient(180deg, rgba(13, 30, 17, 0.92), rgba(4, 11, 7, 0.96)),
    repeating-linear-gradient(
      135deg,
      rgba(125, 255, 178, 0.025) 0 8px,
      transparent 8px 16px
    );
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.38);
  border-radius: 24px;
}

.marque {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
}

.sceau {
  display: grid;
  flex: 0 0 62px;
  width: 62px;
  height: 62px;
  place-items: center;
  border-radius: 20px;
  border: 1px solid rgba(214, 178, 24, 0.72);
  background:
    radial-gradient(circle at 32% 20%, rgba(214, 178, 24, 0.4), transparent 38%),
    linear-gradient(135deg, #122417, #020604);
  color: #d6b218;
  font-family: Georgia, serif;
  font-size: 24px;
  font-weight: 900;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  color: #fff8d6;
  font-size: 22px;
  line-height: 1.05;
}

h2 {
  color: #fff8d6;
  font-size: 17px;
}

.marque p,
.note,
small,
.sur-titre {
  color: #9fb79e;
}

.bloc {
  padding: 16px;
}

.titre-ligne {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

label {
  display: block;
  margin: 14px 0 7px;
  color: #d9edc8;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

select {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid rgba(125, 255, 178, 0.22);
  border-radius: 14px;
  outline: none;
  color: #f5f0d4;
  background: #06110a;
}

select:focus {
  border-color: rgba(214, 178, 24, 0.76);
  box-shadow: 0 0 0 4px rgba(214, 178, 24, 0.12);
}

.segmente {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.segmente button,
.bouton-mini {
  cursor: pointer;
  border: 1px solid rgba(214, 178, 24, 0.2);
  border-radius: 999px;
  color: #d9edc8;
  background: rgba(255, 255, 255, 0.04);
  padding: 9px 11px;
}

.segmente button.actif {
  color: #06110a;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  font-weight: 900;
}

.pastille {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 9px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
}

.pastille.pret {
  color: #07130b;
  background: #7dffb2;
}

.pastille.erreur,
.pastille.verification {
  color: #fff8d6;
  background: rgba(255, 87, 87, 0.2);
}

.point {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: currentColor;
}

.note {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.45;
}

.atelier {
  display: flex;
  flex-direction: column;
  padding: 22px;
}

.bandeau {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.sur-titre {
  margin-bottom: 7px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 11px;
  font-weight: 900;
}

.bandeau h2 {
  font-size: clamp(28px, 4vw, 48px);
  line-height: 0.98;
}

.badge-modele {
  border: 1px solid rgba(214, 178, 24, 0.38);
  border-radius: 999px;
  padding: 10px 14px;
  color: #d6b218;
  font-weight: 950;
  text-transform: uppercase;
}

.zone-fichier {
  display: grid;
  min-height: 330px;
  place-items: center;
  align-content: center;
  gap: 12px;
  margin: 0;
  padding: 28px;
  cursor: pointer;
  text-align: center;
  border: 1px dashed rgba(125, 255, 178, 0.38);
  border-radius: 28px;
  background:
    radial-gradient(circle at center, rgba(125, 255, 178, 0.08), transparent 55%),
    rgba(0, 0, 0, 0.22);
}

.zone-fichier:hover {
  border-color: rgba(214, 178, 24, 0.82);
  background:
    radial-gradient(circle at center, rgba(214, 178, 24, 0.12), transparent 55%),
    rgba(0, 0, 0, 0.26);
}

.zone-fichier input {
  display: none;
}

.icone-upload {
  display: grid;
  width: 74px;
  height: 74px;
  place-items: center;
  border-radius: 24px;
  color: #07130b;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  font-size: 34px;
  font-weight: 900;
}

.zone-fichier strong {
  color: #fff8d6;
  font-size: 24px;
}

.zone-fichier em {
  max-width: 620px;
  color: #9fb79e;
  font-style: normal;
  overflow-wrap: anywhere;
}

.fiche-fichier {
  display: grid;
  grid-template-columns: 1.7fr 0.8fr 0.8fr;
  gap: 12px;
  margin-top: 14px;
}

.fiche-fichier > div {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(125, 255, 178, 0.14);
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.2);
}

.fiche-fichier span {
  display: block;
  margin-bottom: 8px;
  color: #9fb79e;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.fiche-fichier strong {
  display: block;
  overflow: hidden;
  color: #fff8d6;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bouton-principal {
  margin-top: auto;
  cursor: pointer;
  border: 0;
  border-radius: 22px;
  padding: 18px 22px;
  color: #041107;
  background: linear-gradient(135deg, #d6b218 0%, #7dffb2 100%);
  box-shadow: 0 22px 44px rgba(125, 255, 178, 0.14);
  font-size: 18px;
  font-weight: 950;
}

.bouton-principal:disabled {
  cursor: not-allowed;
  opacity: 0.45;
  box-shadow: none;
}

.alerte {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 87, 87, 0.35);
  border-radius: 16px;
  color: #ffd0d0;
  background: rgba(255, 87, 87, 0.1);
}

.panneau-droit .haut {
  flex: 1;
}

.pipeline {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.etape {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border: 1px solid rgba(125, 255, 178, 0.12);
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.18);
}

.etape .numero {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid #4c694d;
}

.etape small {
  display: block;
  margin-top: 3px;
}

.etape.fait .numero {
  border-color: #7dffb2;
  background: #7dffb2;
  box-shadow: 0 0 18px rgba(125, 255, 178, 0.35);
}

.etape.actif {
  border-color: rgba(214, 178, 24, 0.55);
}

.etape.actif .numero {
  border-color: #d6b218;
  box-shadow: 0 0 20px rgba(214, 178, 24, 0.45);
}

.etape.erreur {
  border-color: rgba(255, 87, 87, 0.55);
}

.etape.erreur .numero {
  border-color: #ff5757;
  background: #ff5757;
}

.telechargements {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.telechargements a {
  display: flex;
  justify-content: center;
  border-radius: 16px;
  padding: 12px 14px;
  color: #041107;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  font-weight: 950;
  text-decoration: none;
}

.journal pre {
  max-height: 230px;
  margin: 12px 0 0;
  overflow: auto;
  white-space: pre-wrap;
  border: 1px solid rgba(125, 255, 178, 0.14);
  border-radius: 16px;
  padding: 13px;
  color: #d9edc8;
  background: #020604;
  font-size: 13px;
  line-height: 1.45;
}

@media (max-width: 1180px) {
  .coquille {
    grid-template-columns: 280px 1fr;
  }

  .panneau-droit {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
  }
}

@media (max-width: 860px) {
  .coquille {
    grid-template-columns: 1fr;
    padding: 12px;
  }

  .panneau-droit {
    display: flex;
  }

  .fiche-fichier {
    grid-template-columns: 1fr;
  }

  .zone-fichier {
    min-height: 240px;
  }
}
</style>
