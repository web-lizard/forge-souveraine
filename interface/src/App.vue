<script setup>
import { ref, computed } from 'vue'

const fichierChoisi = ref(null)
const langue = ref('auto')
const modele = ref('base')
const styleSelectionne = ref('imperial')
const journal = ref('Forge Souveraine prete. Choisis une video.')

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
  journal.value = fichier ? 'Fichier choisi: ' + fichier.name : 'Fichier annule.'
}

function lancerForge() {
  if (!fichierChoisi.value) {
    journal.value = 'Choisis une video.'
    return
  }

  journal.value =
    'Preparation locale...' + "\n" +
    'Fichier: ' + fichierChoisi.value.name + "\n" +
    'Langue: ' + langue.value + "\n" +
    'Modele: ' + modele.value + "\n" +
    'Style: ' + styleSelectionne.value + "\n\n" +
    'Backend Python sera branche ensuite.'
}
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

      <button class="principal" @click="lancerForge">
        Forger les sous-titres
      </button>
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

.accroche {
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

.styles button {
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
