<script setup>
import { computed, onMounted, ref } from 'vue'

const adresseServeur = 'http://127.0.0.1:8787'

const langueInterface = ref('fr')
const langue = ref('ru')
const modele = ref('small')
const styleSelectionne = ref('shorts_clean')
const tiroir = ref('')
const phase = ref('idle')
const survolDepot = ref(false)

const etatServeur = ref('verification')
const infosServeur = ref(null)
const fichierSelectionne = ref(null)
const resultatTeleversement = ref(null)
const resultatTache = ref(null)
const resultatExecution = ref(null)
const listeSorties = ref([])
const dossierSorties = ref('')
const forgeEnCours = ref(false)
const erreurInterface = ref('')
const journal = ref('Forge Souveraine attend un fichier.')

const textes = {
  fr: {
    app: 'Forge Souveraine',
    sousTitre: 'Atelier local de sous-titres',
    verifier: 'Verifier',
    apiOk: 'API en ligne',
    apiNon: 'API indisponible',
    local: 'Tout reste local',
    choisir: 'Choisir',
    fichier: 'Fichier',
    reglages: 'Reglages',
    pipeline: 'Pipeline',
    resultats: 'Resultats',
    journal: 'Journal',
    aucun: 'Aucun fichier',
    deposer: 'Choisis une video ou un audio',
    dropCall: 'Glisse le fichier ici',
    dropHint: 'depose: lancement automatique',
    pret: 'Pret a forger',
    megaIdle: 'CHOISIR',
    megaReady: 'FORGER',
    megaWork: 'FORGE',
    megaDone: 'PRET',
    megaHintIdle: 'MP4, MOV, WEBM, MP3, WAV, M4A',
    megaHintReady: 'Lancer transcription et rendu',
    megaHintWork: 'La machine travaille',
    megaHintDone: 'Sorties disponibles',
    langueAudio: 'Langue audio',
    interface: 'Interface',
    modele: 'Modele Whisper',
    style: 'Style des sous-titres',
    styleClean: 'Shorts clean',
    styleGold: 'Imperial gold',
    styleBig: 'Large lisible',
    styleRed: 'Rouge classique',
    styleSoft: 'Soft rounded',
    qualiteNote: 'tiny est rapide mais faible. small est le defaut conseille. Les styles utilisent des polices systeme Windows.',
    auto: 'Auto',
    russe: 'Russe',
    francais: 'Francais',
    anglais: 'Anglais',
    imperial: 'Imperial',
    rapide: 'rapide',
    equilibre: 'equilibre',
    precis: 'plus precis',
    upload: 'Upload',
    tache: 'Tache',
    transcription: 'Whisper',
    rendu: 'Rendu',
    sorties: 'Sorties',
    attente: 'Attente',
    actif: 'Actif',
    fait: 'Fait',
    erreur: 'Erreur',
    taille: 'Taille',
    type: 'Type',
    video: 'Video',
    audio: 'Audio',
    telechargerSrt: 'SRT',
    telechargerAss: 'ASS',
    telechargerJson: 'JSON',
    telechargerMp4: 'MP4',
    pretATravailler: 'Pret a travailler.',
    erreurFichier: 'Choisis d abord un fichier.',
    sauvegarde: 'Upload local...',
    tacheCreee: 'Tache creee. Whisper travaille...',
    premierLancement: 'Premier lancement: le modele peut se telecharger.',
    renduEnCours: 'Sous-titres prets. Rendu MP4...',
    termine: 'Forge terminee.',
    probleme: 'Probleme dans la forge.',
    aucunResultat: 'Les fichiers apparaitront ici.',
    dossierSorties: 'Dossier de sortie',
    ouvrirDossier: 'Ouvrir le dossier',
    actualiser: 'Actualiser',
    historique: 'Historique',
    aucunHistorique: 'Aucun fichier encore.',
    ouvrir: 'Ouvrir',
    fermer: 'Fermer'
  },
  ru: {
    app: 'Forge Souveraine',
    sousTitre: 'Локальная кузница субтитров',
    verifier: 'Проверить',
    apiOk: 'API онлайн',
    apiNon: 'API недоступен',
    local: 'Всё локально',
    choisir: 'Выбрать',
    fichier: 'Файл',
    reglages: 'Настройки',
    pipeline: 'Процесс',
    resultats: 'Результаты',
    journal: 'Журнал',
    aucun: 'Файл не выбран',
    deposer: 'Выбери видео или аудио',
    dropCall: 'Брось файл сюда',
    dropHint: 'отпусти: запуск сразу',
    pret: 'Готово к ковке',
    megaIdle: 'ВЫБРАТЬ',
    megaReady: 'КОВАТЬ',
    megaWork: 'КУЁМ',
    megaDone: 'ГОТОВО',
    megaHintIdle: 'MP4, MOV, WEBM, MP3, WAV, M4A',
    megaHintReady: 'Запустить транскрибацию и рендер',
    megaHintWork: 'Машина работает',
    megaHintDone: 'Файлы готовы',
    langueAudio: 'Язык аудио',
    interface: 'Интерфейс',
    modele: 'Модель Whisper',
    style: 'Стиль субтитров',
    styleClean: 'Чистый Shorts',
    styleGold: 'Имперское золото',
    styleBig: 'Крупный читаемый',
    styleRed: 'Красный классический',
    styleSoft: 'Мягкий округлый',
    qualiteNote: 'tiny быстрый, но слабый. small теперь рекомендуемый дефолт. Стили используют системные шрифты Windows.',
    auto: 'Авто',
    russe: 'Русский',
    francais: 'Французский',
    anglais: 'Английский',
    imperial: 'Имперский',
    rapide: 'быстро',
    equilibre: 'баланс',
    precis: 'точнее',
    upload: 'Загрузка',
    tache: 'Задача',
    transcription: 'Whisper',
    rendu: 'Рендер',
    sorties: 'Файлы',
    attente: 'Ожидание',
    actif: 'Активно',
    fait: 'Готово',
    erreur: 'Ошибка',
    taille: 'Размер',
    type: 'Тип',
    video: 'Видео',
    audio: 'Аудио',
    telechargerSrt: 'SRT',
    telechargerAss: 'ASS',
    telechargerJson: 'JSON',
    telechargerMp4: 'MP4',
    pretATravailler: 'Можно работать.',
    erreurFichier: 'Сначала выбери файл.',
    sauvegarde: 'Локальная загрузка...',
    tacheCreee: 'Задача создана. Whisper работает...',
    premierLancement: 'Первый запуск: модель может скачиваться.',
    renduEnCours: 'Субтитры готовы. Рендер MP4...',
    termine: 'Кузница завершила работу.',
    probleme: 'Проблема в кузнице.',
    aucunResultat: 'Файлы появятся здесь.',
    dossierSorties: 'Папка результатов',
    ouvrirDossier: 'Открыть папку',
    actualiser: 'Обновить',
    historique: 'История',
    aucunHistorique: 'Пока файлов нет.',
    ouvrir: 'Открыть',
    fermer: 'Закрыть'
  }
}

const t = (cle) => textes[langueInterface.value]?.[cle] ?? textes.fr[cle] ?? cle

const etapes = computed(() => [
  { code: 'upload', titre: t('upload') },
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

const etatMega = computed(() => {
  if (forgeEnCours.value) return 'work'
  if (resultatExecution.value?.sorties) return 'done'
  if (fichierSelectionne.value) return 'ready'
  return 'idle'
})

const megaTexte = computed(() => {
  if (etatMega.value === 'work') return t('megaWork')
  if (etatMega.value === 'done') return t('megaDone')
  if (etatMega.value === 'ready') return t('megaReady')
  return t('megaIdle')
})

const megaIndice = computed(() => {
  if (etatMega.value === 'work') return t('megaHintWork')
  if (etatMega.value === 'done') return t('megaHintDone')
  if (etatMega.value === 'ready') return t('megaHintReady')
  return t('megaHintIdle')
})

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

async function chargerSorties() {
  try {
    const reponse = await fetch(adresseServeur + '/api/sorties')

    if (!reponse.ok) {
      throw new Error('Sorties HTTP ' + reponse.status)
    }

    const donnees = await reponse.json()
    listeSorties.value = donnees.fichiers || []
    dossierSorties.value = donnees.dossier || ''
  } catch (erreur) {
    journal.value = t('erreur') + ': ' + erreur.message
  }
}

async function ouvrirDossierSorties() {
  try {
    const reponse = await fetch(adresseServeur + '/api/sorties/ouvrir', {
      method: 'POST'
    })

    if (!reponse.ok) {
      throw new Error('Open folder HTTP ' + reponse.status)
    }

    await chargerSorties()
  } catch (erreur) {
    journal.value = t('erreur') + ': ' + erreur.message
  }
}

function changerTiroir(nom) {
  tiroir.value = tiroir.value === nom ? '' : nom
}

function statutEtape(code) {
  if (resultatTache.value?.etat === 'erreur' || resultatExecution.value?.etat === 'erreur') {
    if (code === 'transcription' && resultatTache.value?.etape === 'transcription_erreur') return 'erreur'
    if (code === 'rendu' && resultatTache.value?.etape === 'rendu_erreur') return 'erreur'
  }

  if (code === 'upload') {
    if (resultatTeleversement.value) return 'fait'
    if (phase.value === 'upload') return 'actif'
    return 'attente'
  }

  if (code === 'tache') {
    if (resultatTache.value) return 'fait'
    if (phase.value === 'tache') return 'actif'
    return 'attente'
  }

  if (code === 'transcription') {
    if (resultatExecution.value?.sorties?.srt) return 'fait'
    if (phase.value === 'transcription') return 'actif'
    return 'attente'
  }

  if (code === 'rendu') {
    if (!estVideo.value) return 'attente'
    if (resultatExecution.value?.sorties?.mp4) return 'fait'
    if (phase.value === 'rendu') return 'actif'
    return 'attente'
  }

  if (code === 'sorties') {
    if (resultatExecution.value?.sorties) return 'fait'
    if (phase.value === 'done') return 'fait'
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

function definirFichier(fichier) {
  fichierSelectionne.value = fichier
  resultatTeleversement.value = null
  resultatTache.value = null
  resultatExecution.value = null
  erreurInterface.value = ''
  phase.value = fichier ? 'ready' : 'idle'

  journal.value = fichier
    ? t('fichier') + ': ' + fichier.name + ' (' + formatOctets(fichier.size) + ')'
    : t('aucun')
}

function choisirFichier(evenement) {
  definirFichier(evenement.target.files?.[0] || null)
}

function gererDragEnter() {
  survolDepot.value = true
}

function gererDragOver() {
  survolDepot.value = true
}

function gererDragLeave(evenement) {
  if (!evenement.currentTarget.contains(evenement.relatedTarget)) {
    survolDepot.value = false
  }
}

async function gererDrop(evenement) {
  survolDepot.value = false

  if (forgeEnCours.value) {
    return
  }

  const fichier = evenement.dataTransfer?.files?.[0] || null

  if (fichier) {
    definirFichier(fichier)
    await forgerSousTitres()
  }
}

function clickMega() {
  if (!fichierSelectionne.value) {
    document.getElementById('entree-fichier')?.click()
    return
  }

  if (!forgeEnCours.value) {
    forgerSousTitres()
  }
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
    phase.value = 'upload'
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

    phase.value = 'tache'
    journal.value = t('sauvegarde') + '\n' + donnees.nom_stocke

    const reponseTache = await fetch(adresseServeur + '/api/taches/creer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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

    phase.value = 'transcription'
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
      phase.value = 'rendu'
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
      phase.value = 'done'
      tiroir.value = 'resultats'
      await chargerSorties()
      journal.value =
        t('termine') + '\n' +
        'Segments: ' + execution.segments + '\n' +
        'Langue: ' + execution.langue_detectee + '\n' +
        'SRT: ' + execution.sorties.srt + '\n' +
        'ASS: ' + execution.sorties.ass + '\n' +
        'JSON: ' + execution.sorties.json +
        (execution.sorties.mp4 ? '\nMP4: ' + execution.sorties.mp4 : '')
    } else {
      phase.value = 'error'
      journal.value =
        t('probleme') + '\n' +
        'Etat: ' + execution.etat + '\n' +
        'Etape: ' + execution.etape + '\n' +
        'Erreur: ' + (execution.erreur || 'inconnue')
    }
  } catch (erreur) {
    phase.value = 'error'
    erreurInterface.value = erreur.message
    journal.value = t('erreur') + ': ' + erreur.message
  } finally {
    forgeEnCours.value = false
  }
}

onMounted(() => {
  verifierServeur()
  chargerSorties()
})
</script>

<template>
  <main
    class="cockpit"
    :class="{ drag: survolDepot }"
    @dragenter.prevent="gererDragEnter"
    @dragover.prevent="gererDragOver"
    @dragleave.prevent="gererDragLeave"
    @drop.prevent="gererDrop"
  >
    <input
      id="entree-fichier"
      class="fichier-cache"
      type="file"
      accept=".mp4,.mov,.mkv,.webm,.m4v,.mp3,.wav,.m4a"
      @change="choisirFichier"
    />

    <div class="drop-overlay" :class="{ visible: survolDepot }">
      <div class="drop-sigil">⬇</div>
      <strong>{{ t('dropCall') }}</strong>
      <span>{{ t('megaHintIdle') }}</span>
    </div>

    <aside class="rail">
      <button class="sigil" type="button" @click="changerTiroir('pipeline')">FS</button>

      <button class="icone" :class="{ actif: tiroir === 'fichier' }" type="button" @click="changerTiroir('fichier')" title="File">▣</button>
      <button class="icone" :class="{ actif: tiroir === 'reglages' }" type="button" @click="changerTiroir('reglages')" title="Settings">⚙</button>
      <button class="icone" :class="{ actif: tiroir === 'pipeline' }" type="button" @click="changerTiroir('pipeline')" title="Pipeline">☷</button>
      <button class="icone" :class="{ actif: tiroir === 'resultats' }" type="button" @click="changerTiroir('resultats')" title="Results">⬇</button>
      <button class="icone" :class="{ actif: tiroir === 'journal' }" type="button" @click="changerTiroir('journal')" title="Journal">⌘</button>
    </aside>

    <section class="scene">
      <header class="topbar">
        <div class="marque">
          <strong>{{ t('app') }}</strong>
          <span>{{ t('sousTitre') }}</span>
        </div>

        <div class="top-actions">
          <button class="etat-api" :class="etatServeur" type="button" @click="verifierServeur">
            <span></span>
            {{ serveurPret ? t('apiOk') : t('apiNon') }}
          </button>

          <div class="lang-switch">
            <button type="button" :class="{ actif: langueInterface === 'fr' }" @click="langueInterface = 'fr'">FR</button>
            <button type="button" :class="{ actif: langueInterface === 'ru' }" @click="langueInterface = 'ru'">RU</button>
          </div>
        </div>
      </header>

      <div class="reacteur-wrap">
        <div class="orbites" :class="etatMega">
          <div class="orbite orbite-a"></div>
          <div class="orbite orbite-b"></div>
          <div class="orbite orbite-c"></div>
          <span class="satellite s1"></span>
          <span class="satellite s2"></span>
          <span class="satellite s3"></span>
        </div>

        <button class="mega" :class="[etatMega, phase]" type="button" :disabled="forgeEnCours && etatMega !== 'work'" @click="clickMega">
          <span class="mega-glow"></span>
          <span class="mega-core">
            <small>{{ t('pret') }}</small>
            <strong>{{ megaTexte }}</strong>
            <em>{{ megaIndice }}</em>
          </span>
        </button>

        <button class="drop-callout" type="button" @click="document.getElementById('entree-fichier')?.click()">
          <strong>{{ t('dropCall') }}</strong>
          <span>{{ t('dropHint') }}</span>
        </button>
      </div>

      <div class="resume">
        <button class="resume-card" type="button" @click="document.getElementById('entree-fichier')?.click()">
          <span>{{ t('fichier') }}</span>
          <strong>{{ nomFichier || t('aucun') }}</strong>
        </button>

        <div class="resume-card">
          <span>{{ t('type') }}</span>
          <strong>{{ estVideo ? t('video') : t('audio') }}</strong>
        </div>

        <div class="resume-card">
          <span>{{ t('taille') }}</span>
          <strong>{{ tailleFichier }}</strong>
        </div>

        <div class="resume-card">
          <span>{{ t('modele') }}</span>
          <strong>{{ modele }}</strong>
        </div>
      </div>

      <p v-if="erreurInterface" class="alerte">{{ erreurInterface }}</p>
    </section>

    <aside class="tiroir" :class="{ ouvert: tiroir }">
      <header class="tiroir-head">
        <h2>
          <span v-if="tiroir === 'fichier'">{{ t('fichier') }}</span>
          <span v-else-if="tiroir === 'reglages'">{{ t('reglages') }}</span>
          <span v-else-if="tiroir === 'resultats'">{{ t('resultats') }}</span>
          <span v-else-if="tiroir === 'journal'">{{ t('journal') }}</span>
          <span v-else>{{ t('pipeline') }}</span>
        </h2>
        <button type="button" @click="tiroir = ''">×</button>
      </header>

      <section v-if="tiroir === 'fichier'" class="panneau">
        <button class="choisir-fichier" type="button" @click="document.getElementById('entree-fichier')?.click()">
          {{ t('choisir') }}
        </button>
        <div class="detail">
          <span>{{ t('fichier') }}</span>
          <strong>{{ nomFichier || t('aucun') }}</strong>
        </div>
        <div class="detail">
          <span>{{ t('taille') }}</span>
          <strong>{{ tailleFichier }}</strong>
        </div>
      </section>

      <section v-else-if="tiroir === 'reglages'" class="panneau">
        <label>{{ t('langueAudio') }}</label>
        <select v-model="langue">
          <option value="auto">{{ t('auto') }}</option>
          <option value="ru">{{ t('russe') }}</option>
          <option value="fr">{{ t('francais') }}</option>
          <option value="en">{{ t('anglais') }}</option>
        </select>

        <label>{{ t('modele') }}</label>
        <select v-model="modele">
          <option value="tiny">tiny, {{ t('rapide') }}</option>
          <option value="base">base, {{ t('equilibre') }}</option>
          <option value="small">small, {{ t('precis') }}</option>
          <option value="medium">medium, quality</option>
        </select>

        <label>{{ t('style') }}</label>
        <select v-model="styleSelectionne">
          <option value="shorts_clean">{{ t('styleClean') }}</option>
          <option value="shorts_gold">{{ t('styleGold') }}</option>
          <option value="shorts_big">{{ t('styleBig') }}</option>
          <option value="shorts_red">{{ t('styleRed') }}</option>
          <option value="shorts_soft">{{ t('styleSoft') }}</option>
        </select>

        <p class="note">{{ t('local') }}</p>
        <p class="note">{{ t('qualiteNote') }}</p>
      </section>

      <section v-else-if="tiroir === 'resultats'" class="panneau">
        <div class="sorties-actions">
          <button type="button" @click="ouvrirDossierSorties">{{ t('ouvrirDossier') }}</button>
          <button type="button" @click="chargerSorties">{{ t('actualiser') }}</button>
        </div>

        <div class="detail chemin-sorties">
          <span>{{ t('dossierSorties') }}</span>
          <strong>{{ dossierSorties || 'D:\ForgeSouveraine\sorties' }}</strong>
        </div>

        <div v-if="resultatExecution?.sorties" class="downloads">
          <a :href="lienSortie(resultatExecution.sorties.srt)" target="_blank">{{ t('telechargerSrt') }}</a>
          <a :href="lienSortie(resultatExecution.sorties.ass)" target="_blank">{{ t('telechargerAss') }}</a>
          <a :href="lienSortie(resultatExecution.sorties.json)" target="_blank">{{ t('telechargerJson') }}</a>
          <a v-if="resultatExecution.sorties.mp4" :href="lienSortie(resultatExecution.sorties.mp4)" target="_blank">{{ t('telechargerMp4') }}</a>
        </div>

        <p v-else class="note">{{ t('aucunResultat') }}</p>

        <h3 class="mini-title">{{ t('historique') }}</h3>

        <div v-if="listeSorties.length" class="historique-sorties">
          <a
            v-for="fichier in listeSorties"
            :key="fichier.nom"
            :href="lienSortie(fichier.nom)"
            target="_blank"
          >
            <strong>{{ fichier.nom }}</strong>
            <span>{{ fichier.extension.toUpperCase() }} · {{ formatOctets(fichier.taille_octets) }}</span>
          </a>
        </div>

        <p v-else class="note">{{ t('aucunHistorique') }}</p>
      </section>

      <section v-else-if="tiroir === 'journal'" class="panneau">
        <pre>{{ journal }}</pre>
      </section>

      <section v-else class="panneau">
        <div class="pipeline">
          <div v-for="etape in etapes" :key="etape.code" class="etape" :class="statutEtape(etape.code)">
            <span class="puce"></span>
            <div>
              <strong>{{ etape.titre }}</strong>
              <small>{{ etiquetteStatut(statutEtape(etape.code)) }}</small>
            </div>
          </div>
        </div>
      </section>
    </aside>
  </main>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(html),
:global(body),
:global(#app) {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  min-width: 0;
  overflow: hidden;
}

:global(body) {
  min-width: 320px;
  background:
    radial-gradient(circle at 48% 42%, rgba(214, 178, 24, 0.14), transparent 26%),
    radial-gradient(circle at 52% 48%, rgba(125, 255, 178, 0.11), transparent 32%),
    linear-gradient(135deg, #020503 0%, #07150b 48%, #020302 100%);
  color: #fff8d6;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

button,
select {
  font: inherit;
}

.cockpit {
  position: relative;
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  width: 100%;
  height: 100dvh;
  overflow: hidden;
}

.fichier-cache {
  display: none;
}

.drop-overlay {
  z-index: 100;
  position: fixed;
  inset: 18px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 14px;
  pointer-events: none;
  opacity: 0;
  transform: scale(0.98);
  transition: opacity 0.18s ease, transform 0.18s ease;
  border: 2px dashed rgba(125, 255, 178, 0.74);
  border-radius: 34px;
  background:
    radial-gradient(circle at center, rgba(125, 255, 178, 0.18), transparent 42%),
    rgba(2, 10, 5, 0.86);
  box-shadow:
    inset 0 0 80px rgba(125, 255, 178, 0.1),
    0 0 90px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  text-align: center;
}

.drop-overlay.visible {
  opacity: 1;
  transform: scale(1);
}

.drop-overlay strong {
  color: #fff8d6;
  font-size: clamp(34px, 6vw, 86px);
  font-weight: 1000;
  letter-spacing: -0.06em;
  text-transform: uppercase;
}

.drop-overlay span {
  color: #d9edc8;
  font-size: 18px;
  font-weight: 900;
}

.drop-sigil {
  display: grid;
  width: 92px;
  height: 92px;
  place-items: center;
  border-radius: 28px;
  color: #041107;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  box-shadow: 0 0 54px rgba(125, 255, 178, 0.25);
  font-size: 44px;
  font-weight: 1000;
}

.cockpit.drag .mega {
  filter: saturate(1.35) brightness(1.08);
  box-shadow:
    0 0 110px rgba(125, 255, 178, 0.28),
    0 0 190px rgba(214, 178, 24, 0.18);
}

.cockpit.drag .scene::before {
  opacity: 1;
}

.drop-callout {
  z-index: 3;
  position: absolute;
  left: 50%;
  bottom: clamp(132px, 14vh, 170px);
  display: grid;
  gap: 4px;
  min-width: 260px;
  transform: translateX(-50%);
  cursor: pointer;
  border: 1px solid rgba(214, 178, 24, 0.32);
  border-radius: 999px;
  padding: 12px 18px;
  color: #fff8d6;
  background:
    linear-gradient(135deg, rgba(214, 178, 24, 0.16), rgba(125, 255, 178, 0.12)),
    rgba(2, 8, 4, 0.78);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
  text-align: center;
}

.drop-callout strong {
  font-size: 15px;
  font-weight: 1000;
  text-transform: uppercase;
}

.drop-callout span {
  color: #9fb79e;
  font-size: 12px;
  font-weight: 850;
}


.rail {
  z-index: 20;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 14px 10px;
  border-right: 1px solid rgba(214, 178, 24, 0.18);
  background:
    linear-gradient(180deg, rgba(3, 9, 5, 0.96), rgba(1, 4, 2, 0.98)),
    repeating-linear-gradient(135deg, rgba(125, 255, 178, 0.035) 0 7px, transparent 7px 14px);
  box-shadow: 18px 0 60px rgba(0, 0, 0, 0.4);
}

.sigil,
.icone {
  display: grid;
  place-items: center;
  cursor: pointer;
  border: 1px solid rgba(214, 178, 24, 0.24);
  background: rgba(255, 255, 255, 0.035);
  color: #d9edc8;
}

.sigil {
  width: 54px;
  height: 54px;
  margin-bottom: 8px;
  border-color: rgba(214, 178, 24, 0.7);
  border-radius: 18px;
  color: #d6b218;
  background:
    radial-gradient(circle at 30% 20%, rgba(214, 178, 24, 0.28), transparent 40%),
    #041107;
  font-family: Georgia, serif;
  font-size: 20px;
  font-weight: 950;
}

.icone {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  font-size: 20px;
}

.icone:hover,
.icone.actif {
  color: #041107;
  border-color: transparent;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  box-shadow: 0 0 34px rgba(125, 255, 178, 0.14);
}

.scene {
  position: relative;
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  min-width: 0;
  height: 100dvh;
  padding: 18px 22px 20px;
  overflow: hidden;
}

.scene::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(rgba(125, 255, 178, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(125, 255, 178, 0.035) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(circle at center, black, transparent 76%);
}

.topbar {
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.marque strong {
  display: block;
  font-size: 18px;
  letter-spacing: 0.04em;
}

.marque span {
  color: #9fb79e;
  font-size: 13px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.etat-api,
.lang-switch,
.lang-switch button {
  border: 1px solid rgba(214, 178, 24, 0.22);
  border-radius: 999px;
  color: #d9edc8;
  background: rgba(2, 8, 4, 0.66);
}

.etat-api {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 13px;
  cursor: pointer;
  font-weight: 850;
}

.etat-api span {
  width: 9px;
  height: 9px;
  border-radius: 99px;
  background: currentColor;
}

.etat-api.pret {
  color: #7dffb2;
}

.etat-api.erreur {
  color: #ff8a8a;
}

.lang-switch {
  display: flex;
  padding: 4px;
}

.lang-switch button {
  cursor: pointer;
  padding: 7px 10px;
  border: 0;
  background: transparent;
  font-weight: 900;
}

.lang-switch button.actif {
  color: #041107;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
}

.reacteur-wrap {
  z-index: 1;
  position: relative;
  display: grid;
  place-items: center;
  min-height: 0;
}

.orbites {
  position: absolute;
  width: min(52vw, 600px);
  aspect-ratio: 1;
  pointer-events: none;
  opacity: 0.72;
}

.orbite {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(214, 178, 24, 0.18);
}

.orbite-a {
  animation: spin 24s linear infinite;
  border-top-color: rgba(214, 178, 24, 0.7);
}

.orbite-b {
  inset: 9%;
  animation: spinReverse 18s linear infinite;
  border-right-color: rgba(125, 255, 178, 0.62);
}

.orbite-c {
  inset: 20%;
  animation: spin 12s linear infinite;
  border-bottom-color: rgba(214, 178, 24, 0.62);
}

.orbites.work .orbite-a,
.orbites.work .orbite-b,
.orbites.work .orbite-c {
  animation-duration: 3.2s;
}

.satellite {
  position: absolute;
  width: 11px;
  height: 11px;
  border-radius: 99px;
  background: #7dffb2;
  box-shadow: 0 0 24px rgba(125, 255, 178, 0.8);
}

.s1 {
  top: 4%;
  left: 50%;
}

.s2 {
  right: 8%;
  top: 62%;
  background: #d6b218;
}

.s3 {
  bottom: 14%;
  left: 18%;
}

.mega {
  position: relative;
  display: grid;
  width: min(38vw, 420px);
  min-width: 300px;
  aspect-ratio: 1;
  place-items: center;
  cursor: pointer;
  border: 0;
  border-radius: 50%;
  color: #fff8d6;
  background:
    conic-gradient(from 180deg, #d6b218, #7dffb2, #123d22, #d6b218);
  box-shadow:
    0 0 90px rgba(125, 255, 178, 0.18),
    0 0 150px rgba(214, 178, 24, 0.12);
}

.mega::before {
  content: "";
  position: absolute;
  inset: 10px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 40%, rgba(125, 255, 178, 0.16), transparent 34%),
    linear-gradient(135deg, #06120a, #020503);
  box-shadow: inset 0 0 58px rgba(0, 0, 0, 0.86);
}

.mega.work {
  animation: megaPulse 1.4s ease-in-out infinite;
}

.mega.work .mega-glow {
  animation: spin 1.6s linear infinite;
  opacity: 1;
}

.mega.done {
  background: conic-gradient(from 180deg, #7dffb2, #d6b218, #7dffb2);
}

.mega:disabled {
  cursor: wait;
}

.mega-glow {
  position: absolute;
  inset: -12px;
  border-radius: 50%;
  opacity: 0.3;
  background: conic-gradient(from 0deg, transparent, rgba(125, 255, 178, 0.8), transparent, rgba(214, 178, 24, 0.8), transparent);
  filter: blur(2px);
}

.mega-core {
  z-index: 2;
  display: grid;
  place-items: center;
  gap: 10px;
  text-align: center;
}

.mega-core small {
  color: #9fb79e;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 12px;
  font-weight: 950;
}

.mega-core strong {
  color: #fff8d6;
  font-size: clamp(46px, 7vw, 86px);
  font-weight: 1000;
  line-height: 0.88;
  letter-spacing: -0.08em;
  text-shadow: 0 8px 42px rgba(0, 0, 0, 0.5);
}

.mega-core em {
  max-width: 250px;
  color: #d9edc8;
  font-style: normal;
  font-weight: 800;
}

.resume {
  z-index: 2;
  display: grid;
  grid-template-columns: minmax(220px, 1.6fr) repeat(3, minmax(130px, 0.7fr));
  gap: 10px;
}

.resume-card {
  min-width: 0;
  border: 1px solid rgba(125, 255, 178, 0.14);
  border-radius: 18px;
  padding: 12px 14px;
  color: #fff8d6;
  background: rgba(2, 8, 4, 0.7);
  text-align: left;
}

button.resume-card {
  cursor: pointer;
}

.resume-card span {
  display: block;
  margin-bottom: 6px;
  color: #9fb79e;
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.resume-card strong {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alerte {
  z-index: 2;
  margin: 12px 0 0;
  padding: 12px;
  border: 1px solid rgba(255, 87, 87, 0.4);
  border-radius: 16px;
  color: #ffd0d0;
  background: rgba(255, 87, 87, 0.12);
}

.tiroir {
  z-index: 15;
  position: absolute;
  top: 18px;
  right: 18px;
  bottom: 18px;
  width: min(390px, calc(100vw - 104px));
  transform: translateX(calc(100% + 26px));
  transition: transform 0.28s ease;
  border: 1px solid rgba(214, 178, 24, 0.24);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(8, 22, 12, 0.96), rgba(2, 7, 4, 0.98)),
    repeating-linear-gradient(135deg, rgba(125, 255, 178, 0.03) 0 8px, transparent 8px 16px);
  box-shadow: -20px 0 80px rgba(0, 0, 0, 0.48);
  overflow: hidden;
}

.tiroir.ouvert {
  transform: translateX(0);
}

.tiroir-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px;
  border-bottom: 1px solid rgba(214, 178, 24, 0.16);
}

.tiroir-head h2 {
  margin: 0;
  font-size: 20px;
}

.tiroir-head button {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  cursor: pointer;
  border: 1px solid rgba(214, 178, 24, 0.22);
  border-radius: 14px;
  color: #d9edc8;
  background: rgba(255, 255, 255, 0.04);
  font-size: 24px;
}

.panneau {
  padding: 18px;
}

.choisir-fichier,
.downloads a {
  display: flex;
  justify-content: center;
  width: 100%;
  cursor: pointer;
  border: 0;
  border-radius: 18px;
  padding: 13px 14px;
  color: #041107;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  font-weight: 950;
  text-decoration: none;
}

.detail {
  margin-top: 12px;
  padding: 13px;
  border: 1px solid rgba(125, 255, 178, 0.14);
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.22);
}

.detail span {
  display: block;
  margin-bottom: 5px;
  color: #9fb79e;
  font-size: 12px;
  text-transform: uppercase;
}

.detail strong {
  overflow-wrap: anywhere;
}

label {
  display: block;
  margin: 14px 0 7px;
  color: #d9edc8;
  font-size: 13px;
  font-weight: 900;
}

select {
  width: 100%;
  border: 1px solid rgba(125, 255, 178, 0.18);
  border-radius: 16px;
  outline: none;
  padding: 12px;
  color: #fff8d6;
  background: #041107;
}

.note {
  color: #9fb79e;
  line-height: 1.5;
}

.pipeline {
  display: grid;
  gap: 10px;
}

.etape {
  display: flex;
  gap: 12px;
  align-items: center;
  border: 1px solid rgba(125, 255, 178, 0.12);
  border-radius: 18px;
  padding: 13px;
  background: rgba(0, 0, 0, 0.2);
}

.puce {
  width: 14px;
  height: 14px;
  border: 2px solid #4c694d;
  border-radius: 99px;
}

.etape strong,
.etape small {
  display: block;
}

.etape small {
  margin-top: 3px;
  color: #9fb79e;
}

.etape.fait .puce {
  border-color: #7dffb2;
  background: #7dffb2;
  box-shadow: 0 0 20px rgba(125, 255, 178, 0.5);
}

.etape.actif {
  border-color: rgba(214, 178, 24, 0.6);
}

.etape.actif .puce {
  border-color: #d6b218;
  box-shadow: 0 0 22px rgba(214, 178, 24, 0.52);
}

.etape.erreur {
  border-color: rgba(255, 87, 87, 0.5);
}

.etape.erreur .puce {
  border-color: #ff5757;
  background: #ff5757;
}

.downloads {
  display: grid;
  gap: 10px;
}

pre {
  max-height: calc(100vh - 140px);
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  border: 1px solid rgba(125, 255, 178, 0.14);
  border-radius: 18px;
  padding: 14px;
  color: #d9edc8;
  background: #020604;
  line-height: 1.5;
}


.sorties-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}

.sorties-actions button {
  cursor: pointer;
  border: 1px solid rgba(214, 178, 24, 0.28);
  border-radius: 16px;
  padding: 11px 12px;
  color: #041107;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  font-weight: 950;
}

.chemin-sorties strong {
  font-size: 12px;
  line-height: 1.35;
}

.mini-title {
  margin: 18px 0 10px;
  color: #fff8d6;
  font-size: 14px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.historique-sorties {
  display: grid;
  gap: 8px;
  max-height: 44vh;
  overflow: auto;
  padding-right: 2px;
}

.historique-sorties a {
  display: grid;
  gap: 4px;
  border: 1px solid rgba(125, 255, 178, 0.13);
  border-radius: 14px;
  padding: 10px 11px;
  color: #fff8d6;
  background: rgba(0, 0, 0, 0.22);
  text-decoration: none;
}

.historique-sorties a:hover {
  border-color: rgba(214, 178, 24, 0.5);
  background: rgba(214, 178, 24, 0.08);
}

.historique-sorties strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
}

.historique-sorties span {
  color: #9fb79e;
  font-size: 12px;
  font-weight: 850;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes spinReverse {
  to {
    transform: rotate(-360deg);
  }
}

@keyframes megaPulse {
  0%,
  100% {
    transform: scale(1);
    filter: saturate(1);
  }

  50% {
    transform: scale(1.025);
    filter: saturate(1.35);
  }
}

@media (max-width: 900px) {
  .cockpit {
    grid-template-columns: 58px 1fr;
  }

  .rail {
    padding: 10px 6px;
  }

  .sigil {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    font-size: 16px;
  }

  .icone {
    width: 42px;
    height: 42px;
  }

  .scene {
    padding: 12px;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .mega {
    width: min(76vw, 380px);
    min-width: 250px;
  }

  .resume {
    grid-template-columns: 1fr 1fr;
  }

  .tiroir {
    right: 10px;
    top: 10px;
    bottom: 10px;
    width: calc(100vw - 78px);
  }
}
</style>
