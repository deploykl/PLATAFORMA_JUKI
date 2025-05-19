<template>
  <div class="container py-3">
    <h2 class="mb-4 fw-bold">ESTABLECIMIENTO</h2>

    <!-- Sección de búsqueda mejorada con autocompletado -->
    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <label class="form-label">Buscar Establecimiento</label>
        <autocomplete :search="searchIpress" placeholder="Escribe nombre o código..."
          aria-label="Buscar establecimiento" @submit="selectIpress">
          <template #result="{ result, props }">
            <li v-bind="props">
              <div class="autocomplete-result">
                <strong>{{ result.NOMBRE }}</strong>
                <small class="text-muted"> Código: {{ result.COD_IPRESS }}</small>
                <small class="d-block">{{ result.DEPARTAMENTO }}</small>
              </div>
            </li>
          </template>
        </autocomplete>
      </div>
    </div>

    <!-- Mostrar datos del establecimiento seleccionado -->
<div v-if="selectedIpress" class="card mb-4">
  <div class="card-body">
    <h5>{{ selectedIpress.nombre }} ({{ selectedIpress.codigo }})</h5>
    <div class="row">
      <div class="col-md-3"><strong>Departamento:</strong> {{ selectedIpress.departamento }}</div>
      <div class="col-md-3"><strong>Provincia:</strong> {{ selectedIpress.provincia }}</div>
      <div class="col-md-3"><strong>Distrito:</strong> {{ selectedIpress.distrito }}</div>
      <div class="col-md-3"><strong>DISA:</strong> {{ selectedIpress.disa }}</div>
    </div>
    
    <!-- Campos adicionales requeridos -->
    <div class="row mt-3">
      <div class="col-md-4">
        <label class="form-label">Categoría *</label>
        <input type="text" class="form-control" v-model="selectedIpress.categoria" required>
      </div>
      <div class="col-md-4">
        <label class="form-label">Responsable</label>
        <input type="text" class="form-control" v-model="selectedIpress.responsable">
      </div>
      <div class="col-md-4">
        <label class="form-label">Monitor</label>
        <input type="text" class="form-control" v-model="selectedIpress.monitor">
      </div>
    </div>
  </div>
</div>

    <!-- Listado ordenado de categorías con preguntas -->
    <div v-for="categoria in sortedCategories" :key="categoria.id" class="mb-5">
      <h3 class="mb-3 border-bottom pb-2">{{ categoria.descripcion }}</h3>

      <div v-if="getSortedPreguntasPorCategoria(categoria.id).length > 0">
        <div v-for="pregunta in getSortedPreguntasPorCategoria(categoria.id)" :key="pregunta.id" class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">{{ pregunta.id }}. {{ pregunta.descripcion }}</h5>

            <div class="btn-group btn-group-toggle w-100 mb-3" role="group">
              <input type="radio" class="btn-check" :id="'si_' + pregunta.id" value="SI"
                v-model="respuestas[pregunta.id].cumplimiento" autocomplete="off">
              <label class="btn btn-outline-success" :for="'si_' + pregunta.id">Sí</label>

              <input type="radio" class="btn-check" :id="'no_' + pregunta.id" value="NO"
                v-model="respuestas[pregunta.id].cumplimiento" autocomplete="off">
              <label class="btn btn-outline-danger" :for="'no_' + pregunta.id">No</label>

              <input type="radio" class="btn-check" :id="'na_' + pregunta.id" value="NA"
                v-model="respuestas[pregunta.id].cumplimiento" autocomplete="off">
              <label class="btn btn-outline-secondary" :for="'na_' + pregunta.id">No aplica</label>
            </div>

            <div class="mb-3">
              <label class="form-label">Observaciones</label>
              <textarea class="form-control" rows="2" v-model="respuestas[pregunta.id].observaciones"></textarea>
            </div>

            <div class="mb-2">
              <label class="form-label">Riesgos/Problemas</label>
              <textarea class="form-control" rows="2" v-model="respuestas[pregunta.id].riesgos_problemas"></textarea>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="alert alert-warning">
        No hay preguntas para esta categoría
      </div>
    </div>

    <!-- Botón de guardar -->
    <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
      <button class="btn btn-primary" @click="guardarRespuestas" :disabled="!canSave || saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
        {{ saving ? 'Guardando...' : 'Guardar Respuestas' }}
      </button>
    </div>

    <div class="text-muted mt-4">
      {{ currentDateTime }}
    </div>
  </div>
</template>

<script setup>
import Autocomplete from '@trevoreyre/autocomplete-vue';
import '@trevoreyre/autocomplete-vue/dist/style.css';
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { debounce } from 'lodash'

// Configuración de Axios
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/ficha/',
  timeout: 5000
})

// Datos reactivos
const searchQuery = ref('')
const selectedIpress = ref(null)
const ipressList = ref([])
const categories = ref([])
const questions = ref([])
const respuestas = ref({})
const loadingQuestions = ref(false)
const saving = ref(false)
const suggestions = ref([])
const showSuggestions = ref(false)
const activeIndex = ref(-1)
const searchInput = ref(null)

// Computed properties
const currentDateTime = computed(() => new Date().toLocaleString())
const canSave = computed(() => selectedIpress.value &&
  Object.values(respuestas.value).some(r => r.cumplimiento !== ''))

// Ordenar categorías por ID ascendente
const sortedCategories = computed(() => {
  return [...categories.value].sort((a, b) => a.id - b.id)
})

// Métodos
const getSortedPreguntasPorCategoria = (categoriaId) => {
  return questions.value
    .filter(pregunta => pregunta.categoria?.id === categoriaId)
    .sort((a, b) => a.id - b.id)
}

const fetchIpress = async () => {
  try {
    const response = await api.get('ipress/')
    ipressList.value = response.data
  } catch (error) {
    console.error('Error al obtener IPRESS:', error)
  }
}

const fetchCategories = async () => {
  try {
    const response = await api.get('categorias-pregunta/')
    categories.value = response.data
  } catch (error) {
    console.error('Error al obtener categorías:', error)
  }
}

const fetchQuestions = async () => {
  loadingQuestions.value = true
  try {
    const response = await api.get('preguntas/')
    questions.value = response.data

    // Inicializar respuestas
    response.data.forEach(pregunta => {
      respuestas.value[pregunta.id] = {
        pregunta: pregunta.id,
        cumplimiento: '',
        puntaje: 0,
        observaciones: '',
        riesgos_problemas: '',
        ipress: selectedIpress.value?.id || null
      }
    })
  } catch (error) {
    console.error('Error al obtener preguntas:', error)
  } finally {
    loadingQuestions.value = false
  }
}

const searchIpress = async (input) => {
  if (!input || input.length < 2) return [];
  
  try {
    const response = await api.get('susalud-proxy/', {
      params: {
        q: input,
        limit: 10
      }
    });
    
    if (!response.data?.result?.records) return [];
    
    const searchLower = input.toLowerCase();
    
    return response.data.result.records
      .filter(item => item.NOMBRE && item.COD_IPRESS) // Solo items con datos válidos
      .map(item => ({
        ...item,
        COD_IPRESS_STR: item.COD_IPRESS.toString() // Convertir código a string una vez
      }))
      .filter(item => 
        item.NOMBRE.toLowerCase().includes(searchLower) || 
        item.COD_IPRESS_STR.includes(input)
      );
  } catch (error) {
    console.error('Error en búsqueda:', error);
    return [];
  }
};

// Modifica el selectIpress para usar el formato del autocomplete
// Selección de IPRESS mejorada
const selectIpress = (result) => {
  if (!result) return;

  selectedIpress.value = {
    // Campos requeridos del modelo Ipress
    nombre: result.NOMBRE || null,
    codigo: result.COD_IPRESS || null,
    categoria: null, // Campo requerido pero no viene de SUSALUD
    departamento: result.DEPARTAMENTO || null,
    provincia: result.PROVINCIA || null,
    disa: result.DISA || null,
    distrito: result.DISTRITO || null,
    
    // Campos de Respuesta que están en tu modelo
    responsable: null,
    monitor: null
  };
}
// Manejar teclado para navegación en sugerencias
const handleKeyDown = (e) => {
  if (!showSuggestions.value || suggestions.value.length === 0) return

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      activeIndex.value = Math.min(activeIndex.value + 1, suggestions.value.length - 1)
      break
    case 'ArrowUp':
      e.preventDefault()
      activeIndex.value = Math.max(activeIndex.value - 1, -1)
      break
    case 'Enter':
      if (activeIndex.value >= 0) {
        e.preventDefault()
        selectIpress(suggestions.value[activeIndex.value])
      }
      break
    case 'Escape':
      showSuggestions.value = false
      break
  }
}

const guardarRespuestas = async () => {
  if (!canSave.value || !selectedIpress.value) return;

  if (!selectedIpress.value.categoria) {
    alert('La categoría es requerida');
    return;
  }

  saving.value = true;

  try {
    // 1. Manejo del IPRESS
    let ipressId;
    try {
      const searchResponse = await api.get(`ipress/?codigo__exact=${selectedIpress.value.codigo}`);
      
      if (searchResponse.data.results?.length > 0) {
        ipressId = searchResponse.data.results[0].id;
      } else {
        const ipressData = {
          nombre: selectedIpress.value.nombre,
          codigo: selectedIpress.value.codigo,
          categoria: selectedIpress.value.categoria,
          departamento: selectedIpress.value.departamento,
          provincia: selectedIpress.value.provincia,
          distrito: selectedIpress.value.distrito,
          disa: selectedIpress.value.disa
        };

        const createResponse = await api.post('ipress/', ipressData);
        ipressId = createResponse.data.id;
      }
    } catch (error) {
      console.error('Error al manejar IPRESS:', error.response?.data || error);
      throw new Error('No se pudo registrar el establecimiento: ' + (error.response?.data?.detail || error.message));
    }

    // 2. Preparar respuestas con valores por defecto para campos requeridos
    const respuestasParaEnviar = Object.values(respuestas.value)
      .filter(r => r.cumplimiento && r.cumplimiento !== '')
      .map(r => ({
        ipress: ipressId,
        pregunta: r.pregunta,
        cumplimiento: r.cumplimiento,
        puntaje: calcularPuntaje(r.cumplimiento),
        observaciones: r.observaciones || null,
        riesgos_problemas: r.riesgos_problemas || null,
        responsable: selectedIpress.value.responsable || "Por definir",
        monitor: selectedIpress.value.monitor || "Por definir",
        fecha: new Date().toISOString() // Asegura que haya una fecha
      }));

    // 3. Enviar respuestas una por una para mejor manejo de errores
    const respuestasGuardadas = [];
    const errores = [];
    
    for (const respuesta of respuestasParaEnviar) {
      try {
        const response = await api.post('respuestas/', respuesta);
        respuestasGuardadas.push(response.data);
      } catch (error) {
        console.error('Error al guardar respuesta:', error.response?.data || error);
        errores.push({
          pregunta: respuesta.pregunta,
          error: error.response?.data || error.message
        });
      }
    }

    if (errores.length > 0) {
      console.error('Errores al guardar:', errores);
      alert(`Se guardaron ${respuestasGuardadas.length} de ${respuestasParaEnviar.length} respuestas. Revise la consola para detalles.`);
    } else {
      alert('¡Todas las respuestas se guardaron correctamente!');
    }

  } catch (error) {
    console.error('Error general:', error);
    alert(`Error: ${error.message}`);
  } finally {
    saving.value = false;
  }
};
// Función auxiliar para calcular puntaje basado en la respuesta
const calcularPuntaje = (cumplimiento) => {
  switch(cumplimiento) {
    case 'SI': return 1;
    case 'NO': return 0;
    case 'NA': return 0.5;
    default: return 0;
  }
};

// Inicialización
onMounted(async () => {
  await Promise.all([fetchIpress(), fetchCategories(), fetchQuestions()])
  window.addEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.card {
  border-left: 4px solid #0d6efd;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.btn-group-toggle {
  display: flex;
}

.btn-group-toggle label {
  flex: 1;
  text-align: center;
}
</style>