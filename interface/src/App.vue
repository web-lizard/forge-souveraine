<script setup>
import { ref, computed, onMounted } from 'vue'

const fichierChoisi = ref(null)
const langue = ref('auto')
const modele = ref('base')
const styleSelectionne = ref('imperial')
const journal = ref('Forge Souveraine prete. Choisis une video.')

const adresseServeur = 'http://127.0.0.1:8787'
const etatServeur = ref('verification')
const messageServeur = ref('Connexion au serveur local...')
const resultatTeleversement = ref(null)
const resultatTache = ref(null)
const resultatExecution = ref(null)
const forgeEnCours = ref(false)

const nomFichier = computed(() => {
  return fichierChoisi.value ? fichierChoisi.value.name : 'Fichier non choisi'
})

const stylesDisponibles = [
  { id: 'imperial', nom: 'Imperial' },
  { id: 'minimal', nom: 'Minimal' },
  { id: 'toxique', nom: 'Toxique' },
  { id: 'scientifique', nom: 'Scientifique' }
]

function choisirFichier(evenement) {
  const fichier = evenement.target.files && evenement.target.files[0]
  fichierChoisi.value = fichier || null
  resultatTeleversement.value = null
  resultatTache.value = null
  resultatExecution.value = null
  journal.value = fichier ? 'Fichier choisi: ' + fichier.name : 'Fichier annule.'
}

async function verifierServeur() {
  try {
    const reponse = await fetch(adresseServeur + '/api/sante')
    const donnees = await reponse.json()

    etatServeur.value = donnees.ok ? 'pret' : 'erreur'
    messageServeur.value = donnees.ok
      ? 'Backend pret: ' + donnees.nom
      : 'Backend repond, mais etat inattendu.'
  } catch (erreur) {
    etatServeur.value = 'hors-ligne'
    messageServeur.value = 'Backend hors ligne. Lance le serveur Python sur le port 8787.'
  }
}

async function lancerForge() {
  if (!fichierChoisi.value) {
    journal.value = 'Choisis une video.'
    return
  }

  forgeEnCours.value = true
  resultatTeleversement.value = null
  resultatTache.value = null
  resultatExecution.value = null

  try {
    journal.value =
      'Televersement vers le backend local...' + "\n" +
      'Fichier: ' + fichierChoisi.value.name + "\n" +
      'Langue: ' + langue.value + "\n" +
      'Modele: ' + modele.value + "\n" +
      'Style: ' + styleSelectionne.value

    const corps = new FormData()
    corps.append('fichier', fichierChoisi.value)

    const reponse = await fetch(adresseServeur + '/api/televerser', {
      method: 'POST',
      body: corps
    })

    if (!reponse.ok) {
      const texteErreur = await reponse.text()
      throw new Error(texteErreur)
    }

    const donnees = await reponse.json()
    resultatTeleversement.value = donnees

    journal.value =
      'Fichier sauvegarde. Creation de la tache...' + "\n" +
      'Nom stocke: ' + donnees.nom_stocke

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
      'Tache creee. Transcription en cours...' + "\n" +
      'ID: ' + tache.identifiant_tache + "\n" +
      'Fichier: ' + tache.nom_stocke + "\n\n" +
      'Premier lancement peut telecharger le modele Whisper.'

    const reponseExecution = await fetch(
      adresseServeur + '/api/taches/' + tache.identifiant_tache + '/executer',
      { method: 'POST' }
    )

    if (!reponseExecution.ok) {
      const texteErreurExecution = await reponseExecution.text()
      throw new Error(texteErreurExecution)
    }

    const execution = await reponseExecution.json()
    resultatExecution.value = execution
    resultatTache.value = execution

    if (execution.etat === 'terminee') {
      journal.value =
        'Transcription terminee.' + "\n" +
        'Segments: ' + execution.segments + "\n" +
        'Langue detectee: ' + execution.langue_detectee + "\n" +
        'SRT: ' + execution.sorties.srt + "\n" +
        'ASS: ' + execution.sorties.ass + "\n" +
        'JSON: ' + execution.sorties.json
    } else {
      journal.value =
        'La tache est terminee avec probleme.' + "\n" +
        'Etat: ' + execution.etat + "\n" +
        'Etape: ' + execution.etape + "\n" +
        'Erreur: ' + (execution.erreur || 'inconnue')
    }

  } catch (erreur) {
    journal.value = 'Erreur pendant le televersement: ' + erreur.message
  } finally {
    forgeEnCours.value = false
  }
}

function lienSortie(nomFichier) {
  return adresseServeur + '/api/sorties/' + encodeURIComponent(nomFichier)
}

onMounted(() => {
  verifierServeur()
})
</script>

<template>
  <main class="coquille">
    <section class="heros">
      <p class="surtitre">Forge Souveraine</p>
      <h1>Имперская кузня субтитров</h1>
      <p class="accroche">
        Локальный генератор субтитров для Shorts: видео, транскрибация, SRT, ASS и будущий MP4-рендер.
      </p>
    </section>

    <section class="carte etat" :class="etatServeur">
      <h2>Etat du serveur</h2>
      <p>{{ messageServeur }}</p>
      <button class="secondaire" @click="verifierServeur">Verifier encore</button>
    </section>

    <section class="carte">
      <h2>1. Video source</h2>

      <label class="zone">
        <input type="file" accept="video/*,audio/*" @change="choisirFichier">
        <span>{{ nomFichier }}</span>
      </label>

      <div class="champs">
        <label>
          Langue
          <select v-model="langue">
            <option value="auto">auto</option>
            <option value="ru">ru</option>
            <option value="en">en</option>
            <option value="fr">fr</option>
          </select>
        </label>

        <label>
          Modele
          <select v-model="modele">
            <option value="tiny">tiny</option>
            <option value="base">base</option>
            <option value="small">small</option>
            <option value="medium">medium</option>
          </select>
        </label>
      </div>

      <div class="styles">
        <button
          v-for="style in stylesDisponibles"
          :key="style.id"
          :class="{ actif: styleSelectionne === style.id }"
          @click="styleSelectionne = style.id"
        >
          {{ style.nom }}
        </button>
      </div>

      <button class="principal" :disabled="forgeEnCours" @click="lancerForge">
        {{ forgeEnCours ? 'Televersement...' : 'Forger les sous-titres' }}
      </button>
    </section>

    <section v-if="resultatTeleversement" class="carte succes">
      <h2>Fichier local sauvegarde</h2>
      <p><strong>Original:</strong> {{ resultatTeleversement.nom_original }}</p>
      <p><strong>Stocke:</strong> {{ resultatTeleversement.nom_stocke }}</p>
      <p><strong>Taille:</strong> {{ resultatTeleversement.taille_octets }} octets</p>
    </section>

    <section v-if="resultatTache" class="carte succes">
      <h2>Tache de transcription</h2>
      <p><strong>ID:</strong> {{ resultatTache.identifiant_tache }}</p>
      <p><strong>Etat:</strong> {{ resultatTache.etat }}</p>
      <p><strong>Etape:</strong> {{ resultatTache.etape }}</p>
      <p><strong>Modele:</strong> {{ resultatTache.modele }}</p>
      <p><strong>Style:</strong> {{ resultatTache.style }}</p>
    </section>

    <section v-if="resultatExecution && resultatExecution.sorties" class="carte succes">
      <h2>Sorties pretes</h2>
      <div class="telechargements">
        <a :href="lienSortie(resultatExecution.sorties.srt)" target="_blank">Telecharger SRT</a>
        <a :href="lienSortie(resultatExecution.sorties.ass)" target="_blank">Telecharger ASS</a>
        <a :href="lienSortie(resultatExecution.sorties.json)" target="_blank">Telecharger JSON</a>
      </div>
    </section>

    <section class="carte">
      <h2>Journal</h2>
      <pre>{{ journal }}</pre>
    </section>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  min-height: 100vh;
  color: #effff5;
  background:
    radial-gradient(circle at top left, rgba(125, 255, 178, .16), transparent 34rem),
    radial-gradient(circle at top right, rgba(112, 92, 255, .22), transparent 30rem),
    linear-gradient(135deg, #030706, #07110d 45%, #10102a);
  font-family: Inter, Segoe UI, system-ui, sans-serif;
}

.coquille {
  width: min(980px, calc(100% - 32px));
  margin: 0 auto;
  padding: 42px 0;
}

.heros,
.carte {
  border: 1px solid rgba(125, 255, 178, .18);
  border-radius: 28px;
  background: rgba(8, 23, 17, .84);
  box-shadow: 0 24px 80px rgba(0, 0, 0, .34);
  padding: 28px;
  margin-bottom: 20px;
}

.surtitre {
  margin: 0 0 12px;
  color: #7dffb2;
  font-weight: 900;
  letter-spacing: .18em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(38px, 7vw, 72px);
  line-height: .95;
}

h2 {
  margin: 0 0 18px;
}

.accroche,
.etat p,
.succes p {
  color: #aac8b7;
  font-size: 18px;
  line-height: 1.55;
}

.zone {
  display: grid;
  gap: 12px;
  min-height: 120px;
  place-items: center;
  border: 1px dashed rgba(125, 255, 178, .42);
  border-radius: 20px;
  background: rgba(0, 0, 0, .22);
  padding: 22px;
}

.champs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0;
}

label {
  color: #aac8b7;
  font-weight: 800;
}

select,
button {
  border: 1px solid rgba(125, 255, 178, .22);
  border-radius: 14px;
  font: inherit;
}

select {
  display: block;
  width: 100%;
  margin-top: 8px;
  padding: 12px;
  color: #effff5;
  background: rgba(14, 40, 30, .95);
}

.styles {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.styles button,
.secondaire {
  padding: 10px 14px;
  color: #effff5;
  background: rgba(0, 0, 0, .22);
  cursor: pointer;
}

.styles button.actif {
  color: #031107;
  background: #7dffb2;
}

.principal {
  width: 100%;
  padding: 15px 18px;
  color: #031107;
  background: linear-gradient(135deg, #7dffb2, #4fd6ff);
  border: 0;
  font-weight: 950;
  cursor: pointer;
}

.principal:disabled {
  opacity: .55;
  cursor: progress;
}

.etat.pret,
.succes {
  border-color: rgba(125, 255, 178, .65);
}

.etat.hors-ligne,
.etat.erreur {
  border-color: rgba(255, 125, 125, .65);
}

.telechargements {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.telechargements a {
  display: inline-flex;
  padding: 10px 14px;
  border-radius: 999px;
  color: #031107;
  background: linear-gradient(135deg, #d6b218, #7dffb2);
  font-weight: 900;
  text-decoration: none;
}

pre {
  min-height: 120px;
  margin: 0;
  padding: 16px;
  border-radius: 18px;
  color: #dfffe9;
  background: rgba(0, 0, 0, .32);
  white-space: pre-wrap;
}
</style>
