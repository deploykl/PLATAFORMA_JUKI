<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-primary">EVALUACIÓN DE ESTABLECIMIENTO</h2>
      <div class="text-muted text-end">
        <small class="d-block">{{ currentDateTime }}</small>
      </div>
    </div>

    <!-- Sección de búsqueda -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5 class="card-title text-primary mb-3">Buscar Establecimiento</h5>
        <div class="autocomplete-wrapper">
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control form-control-lg" v-model="searchQuery" @input="handleSearchInput"
              @keydown="handleKeyDown" placeholder="Escribe nombre o código del establecimiento..." ref="searchInput">
            <button v-if="searchQuery" class="btn btn-outline-secondary" @click="clearSearch">
              <i class="bi bi-x"></i>
            </button>
          </div>
          <ul class="autocomplete-results" v-if="showSuggestions && suggestions.length > 0">
            <li v-for="(result, index) in suggestions" :key="index" @click="selectIpress(result)"
              :class="{ 'active': index === activeIndex }">
              <div class="autocomplete-result">
                <strong>{{ result.NOMBRE }}</strong>
                <div class="d-flex justify-content-between">
                  <small class="text-muted">Código: {{ result.COD_IPRESS }}</small>
                  <small class="text-muted">{{ result.DEPARTAMENTO }} - {{ result.PROVINCIA }}</small>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Datos del establecimiento seleccionado -->
    <div v-if="selectedIpress" class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h4 class="text-primary mb-1">{{ selectedIpress.nombre }}</h4>
            <div class="d-flex flex-wrap gap-2 mb-2">
              <span class="badge bg-primary">Código: {{ selectedIpress.codigo }}</span>
              <span class="badge bg-secondary">Categoría: {{ selectedIpress.categoria || 'No especificada' }}</span>
            </div>
          </div>
          <button class="btn btn-sm btn-outline-danger" @click="clearSelection">
            <i class="bi bi-x-circle"></i> Cambiar
          </button>
        </div>

        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label fw-bold">Departamento</label>
            <div class="form-control-plaintext">{{ selectedIpress.departamento }}</div>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">Provincia</label>
            <div class="form-control-plaintext">{{ selectedIpress.provincia }}</div>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">Distrito</label>
            <div class="form-control-plaintext">{{ selectedIpress.distrito }}</div>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">DISA</label>
            <div class="form-control-plaintext">{{ selectedIpress.disa }}</div>
          </div>

          <div class="col-md-6">
            <label class="form-label fw-bold">Responsable <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model="selectedIpress.responsable" required>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-bold">Monitor <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model="selectedIpress.monitor" required>
          </div>
        </div>
      </div>
    </div>

   <!-- Sidebar flotante para categorías -->
    <div class="evaluation-sidebar" :class="{
      'sidebar-collapsed': sidebarCollapsed,
      'mobile-sidebar': isMobile
    }">
      <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
        <i class="bi" :class="sidebarCollapsed ? 'bi-chevron-left' : 'bi-chevron-right'"></i>
      </button>
      
      <div class="sidebar-content">
        <div class="sidebar-header">
          <h5>Categorías</h5>
        </div>
        <div class="sidebar-categories">
          <div 
            v-for="categoria in sortedCategories" 
            :key="categoria.id"
            class="sidebar-category"
            :class="{ 
              'active': activeCategory === categoria.id,
              'completed': getPreguntasCompletadas(categoria.id) === getSortedPreguntasPorCategoria(categoria.id).length
            }"
            @click="scrollToCategory(categoria.id)"
          >
            <span>{{ categoria.descripcion }}</span>
            <small>{{ getPreguntasCompletadas(categoria.id) }}/{{ getSortedPreguntasPorCategoria(categoria.id).length }}</small>
          </div>
        </div>
      </div>
      
      <!-- Mini versión para móvil -->
      <div class="mobile-sidebar-handle" @click="sidebarCollapsed = !sidebarCollapsed">
        <div class="progress-indicator">
          {{ totalRespondidas }}/{{ totalPreguntas }}
        </div>
      </div>
    </div>

    <!-- Resumen flotante -->
    <div class="floating-summary" :class="{ 'visible': selectedIpress }">
      <div class="summary-content">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h5 class="mb-1">Resumen</h5>
            <p class="mb-0 text-muted">
              {{ totalRespondidas }}/{{ totalPreguntas }} ({{ porcentajeCompletado }}%)
            </p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-danger" @click="clearAllAnswers" :disabled="totalRespondidas === 0"
              title="Limpiar todo">
              <i class="bi bi-trash"></i>
            </button>
            <button class="btn btn-sm btn-primary" @click="guardarRespuestas" :disabled="!canSave || saving"
              title="Guardar">
              <template v-if="saving">
                <span class="spinner-border spinner-border-sm me-1"></span>
              </template>
              <template v-else>
                <i class="bi bi-save"></i>
              </template>
            </button>
          </div>
        </div>
        <div class="progress mt-2" style="height: 5px;">
          <div class="progress-bar bg-success" role="progressbar" :style="{ width: porcentajeCompletado + '%' }"
            :aria-valuenow="porcentajeCompletado" aria-valuemin="0" aria-valuemax="100">
          </div>
        </div>
      </div>
    </div>

    <!-- Contenedor principal de categorías -->
    <div class="categories-container">
      <!-- Listado de categorías con preguntas -->
      <div v-for="(categoria, index) in sortedCategories" :key="categoria.id" class="mb-4 category-section"
        :id="'category-' + categoria.id">
        <div class="card shadow-sm">
          <div class="card-header bg-light cursor-pointer" @click="toggleCategory(categoria.id)">
            <div class="d-flex justify-content-between align-items-center">
              <h3 class="h5 mb-0">
                <i class="bi"
                  :class="collapsedCategories.includes(categoria.id) ? 'bi-chevron-right' : 'bi-chevron-down'"></i>
                {{ categoria.descripcion }}
              </h3>
              <span class="badge bg-primary">
                {{ getPreguntasCompletadas(categoria.id) }} / {{ getSortedPreguntasPorCategoria(categoria.id).length }}
              </span>
            </div>
          </div>

          <div class="card-body" v-if="!collapsedCategories.includes(categoria.id)">
            <div v-if="getSortedPreguntasPorCategoria(categoria.id).length > 0">
              <div v-for="pregunta in getSortedPreguntasPorCategoria(categoria.id)" :key="pregunta.id"
                class="mb-4 pb-3 border-bottom">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h5 class="mb-0">
                    <span class="text-muted me-2">{{ pregunta.id }}.</span>
                    {{ pregunta.descripcion }}
                  </h5>
                  <button class="btn btn-sm btn-outline-danger" @click="clearAnswer(pregunta.id)">
                    <i class="bi bi-arrow-counterclockwise"></i>
                  </button>
                </div>

                <div class="btn-group btn-group-toggle w-100 mb-3" role="group">
                  <input type="radio" class="btn-check" :id="'si_' + pregunta.id" value="SI"
                    v-model="respuestas[pregunta.id].cumplimiento" autocomplete="off">
                  <label class="btn btn-outline-success" :for="'si_' + pregunta.id">
                    <i class="bi bi-check-circle"></i> Sí
                  </label>

                  <input type="radio" class="btn-check" :id="'no_' + pregunta.id" value="NO"
                    v-model="respuestas[pregunta.id].cumplimiento" autocomplete="off">
                  <label class="btn btn-outline-danger" :for="'no_' + pregunta.id">
                    <i class="bi bi-x-circle"></i> No
                  </label>

                  <input type="radio" class="btn-check" :id="'na_' + pregunta.id" value="NA"
                    v-model="respuestas[pregunta.id].cumplimiento" autocomplete="off">
                  <label class="btn btn-outline-secondary" :for="'na_' + pregunta.id">
                    <i class="bi bi-dash-circle"></i> No aplica
                  </label>
                </div>

                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label fw-bold">Observaciones</label>
                    <textarea class="form-control" rows="2" v-model="respuestas[pregunta.id].observaciones"
                      placeholder="Ingrese observaciones relevantes..."></textarea>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-bold">Riesgos/Problemas identificados</label>
                    <textarea class="form-control" rows="2" v-model="respuestas[pregunta.id].riesgos_problemas"
                      placeholder="Describa los riesgos o problemas encontrados..."></textarea>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="alert alert-warning mb-0">
              No hay preguntas para esta categoría
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import axios from 'axios'
import { debounce } from 'lodash'

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
const collapsedCategories = ref([])
const sidebarCollapsed = ref(false)
const activeCategory = ref(null)

// Computed properties
const currentDateTime = computed(() => {
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }
  return new Date().toLocaleDateString('es-ES', options)
})

const canSave = computed(() => {
  return selectedIpress.value &&
    selectedIpress.value.responsable &&
    selectedIpress.value.monitor &&
    totalRespondidas.value > 0
})

const sortedCategories = computed(() => {
  return [...categories.value].sort((a, b) => a.id - b.id)
})

const totalPreguntas = computed(() => questions.value.length)

const totalRespondidas = computed(() => {
  return Object.values(respuestas.value).filter(r => r.cumplimiento !== '').length
})

const porcentajeCompletado = computed(() => {
  return Math.round((totalRespondidas.value / totalPreguntas.value) * 100)
})

// Métodos
const getSortedPreguntasPorCategoria = (categoriaId) => {
  return questions.value
    .filter(pregunta => pregunta.categoria?.id === categoriaId)
    .sort((a, b) => a.id - b.id)
}

const getPreguntasCompletadas = (categoriaId) => {
  return getSortedPreguntasPorCategoria(categoriaId)
    .filter(pregunta => respuestas.value[pregunta.id]?.cumplimiento !== '')
    .length
}

const toggleCategory = (categoryId) => {
  const index = collapsedCategories.value.indexOf(categoryId)
  if (index === -1) {
    collapsedCategories.value.push(categoryId)
  } else {
    collapsedCategories.value.splice(index, 1)
  }

  // Si la categoría se está abriendo, actualizar la categoría activa
  if (index !== -1) {
    nextTick(() => {
      scrollToCategory(categoryId)
    })
  }
}

const scrollToCategory = (categoryId) => {
  const element = document.getElementById(`category-${categoryId}`)
  if (element) {
    activeCategory.value = categoryId
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })

    // Si la categoría está colapsada, abrirla
    if (collapsedCategories.value.includes(categoryId)) {
      collapsedCategories.value = collapsedCategories.value.filter(id => id !== categoryId)
    }
  }
}

const handleScroll = debounce(() => {
  if (sidebarCollapsed.value) return

  const categorySections = document.querySelectorAll('.category-section')
  let currentActive = null

  categorySections.forEach(section => {
    const rect = section.getBoundingClientRect()
    if (rect.top <= 100 && rect.bottom >= 100) {
      currentActive = section.id.replace('category-', '')
    }
  })

  if (currentActive && currentActive !== activeCategory.value) {
    activeCategory.value = currentActive
  }
}, 100)

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
      .filter(item => item.NOMBRE && item.COD_IPRESS)
      .map(item => ({
        ...item,
        COD_IPRESS_STR: item.COD_IPRESS.toString()
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

const handleSearchInput = debounce(async () => {
  if (searchQuery.value.length < 2) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }

  suggestions.value = await searchIpress(searchQuery.value)
  showSuggestions.value = true
  activeIndex.value = -1
}, 300)

const selectIpress = (result) => {
  if (!result) return;

  selectedIpress.value = {
    nombre: result.NOMBRE || null,
    codigo: result.COD_IPRESS || null,
    categoria: result.CATEGORIA || null,
    departamento: result.DEPARTAMENTO || null,
    provincia: result.PROVINCIA || null,
    disa: result.DISA || null,
    distrito: result.DISTRITO || null,
    responsable: null,
    monitor: null
  };

  // Resetear búsqueda
  searchQuery.value = ''
  suggestions.value = []
  showSuggestions.value = false

  // Expandir solo la primera categoría al seleccionar un establecimiento
  if (sortedCategories.value.length > 0) {
    collapsedCategories.value = sortedCategories.value.slice(1).map(c => c.id)
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  suggestions.value = []
  showSuggestions.value = false
}

const clearSelection = () => {
  selectedIpress.value = null
  // Limpiar todas las respuestas
  Object.keys(respuestas.value).forEach(key => {
    respuestas.value[key] = {
      pregunta: key,
      cumplimiento: '',
      puntaje: 0,
      observaciones: '',
      riesgos_problemas: '',
      ipress: null
    }
  })
}

const clearAnswer = (preguntaId) => {
  if (respuestas.value[preguntaId]) {
    respuestas.value[preguntaId] = {
      pregunta: preguntaId,
      cumplimiento: '',
      puntaje: 0,
      observaciones: '',
      riesgos_problemas: '',
      ipress: selectedIpress.value?.id || null
    }
  }
}

const clearAllAnswers = () => {
  if (confirm('¿Está seguro que desea limpiar todas las respuestas?')) {
    Object.keys(respuestas.value).forEach(key => {
      respuestas.value[key] = {
        pregunta: key,
        cumplimiento: '',
        puntaje: 0,
        observaciones: '',
        riesgos_problemas: '',
        ipress: selectedIpress.value?.id || null
      }
    })
  }
}

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

  if (!selectedIpress.value.responsable || !selectedIpress.value.monitor) {
    alert('Los campos de Responsable y Monitor son obligatorios');
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

    // 2. Preparar respuestas
    const respuestasParaEnviar = Object.values(respuestas.value)
      .filter(r => r.cumplimiento && r.cumplimiento !== '')
      .map(r => ({
        ipress: ipressId,
        pregunta: r.pregunta,
        cumplimiento: r.cumplimiento,
        puntaje: calcularPuntaje(r.cumplimiento),
        observaciones: r.observaciones || null,
        riesgos_problemas: r.riesgos_problemas || null,
        responsable: selectedIpress.value.responsable,
        monitor: selectedIpress.value.monitor,
        fecha: new Date().toISOString()
      }));

    // 3. Enviar respuestas en lotes para mejor performance
    const batchSize = 10;
    const batches = [];
    for (let i = 0; i < respuestasParaEnviar.length; i += batchSize) {
      batches.push(respuestasParaEnviar.slice(i, i + batchSize));
    }

    const respuestasGuardadas = [];
    const errores = [];

    for (const batch of batches) {
      try {
        const responses = await Promise.all(
          batch.map(respuesta => api.post('respuestas/', respuesta))
        );
        respuestasGuardadas.push(...responses.map(r => r.data));
      } catch (error) {
        console.error('Error al guardar lote de respuestas:', error);
        errores.push(...batch.map(r => ({
          pregunta: r.pregunta,
          error: error.response?.data || error.message
        })));
      }
    }

    if (errores.length > 0) {
      console.error('Errores al guardar:', errores);
      alert(`Se guardaron ${respuestasGuardadas.length} de ${respuestasParaEnviar.length} respuestas. Revise la consola para detalles.`);
    } else {
      alert('¡Evaluación guardada correctamente!');
      // Opcional: redireccionar o resetear el formulario
    }

  } catch (error) {
    console.error('Error general:', error);
    alert(`Error: ${error.message}`);
  } finally {
    saving.value = false;
  }
};

const calcularPuntaje = (cumplimiento) => {
  switch (cumplimiento) {
    case 'SI': return 1;
    case 'NO': return 0;
    case 'NA': return 0.5;
    default: return 0;
  }
};
const isMobile = ref(false)

const checkIfMobile = () => {
  isMobile.value = window.innerWidth <= 768
}
// En onMounted añade:
onMounted(async () => {
  await Promise.all([fetchIpress(), fetchCategories(), fetchQuestions()])
  window.addEventListener('scroll', handleScroll)
  checkIfMobile()
  window.addEventListener('resize', checkIfMobile)
  
  if (sortedCategories.value.length > 0) {
    collapsedCategories.value = sortedCategories.value.slice(1).map(c => c.id)
  }
})

// En onUnmounted añade:
onUnmounted(() => {
  window.removeEventListener('resize', checkIfMobile)
  window.removeEventListener('scroll', handleScroll)
})

// Observar cambios en el establecimiento seleccionado
watch(selectedIpress, (newVal) => {
  if (newVal) {
    // Actualizar el ipress en todas las respuestas
    Object.keys(respuestas.value).forEach(key => {
      respuestas.value[key].ipress = newVal.id || null
    })
  }
})
</script>

<style scoped>
.card {
  border: none;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.card-header {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.card-header:hover {
  background-color: #f8f9fa !important;
}

.btn-group-toggle {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-group-toggle label {
  flex: 1;
  min-width: 100px;
  text-align: center;
  border-radius: 0.375rem !important;
}

.btn-outline-success:hover,
.btn-check:checked+.btn-outline-success {
  background-color: var(--bs-success);
  color: white;
}

.btn-outline-danger:hover,
.btn-check:checked+.btn-outline-danger {
  background-color: var(--bs-danger);
  color: white;
}

.btn-outline-secondary:hover,
.btn-check:checked+.btn-outline-secondary {
  background-color: var(--bs-secondary);
  color: white;
}

/* Estilos para el autocomplete */
.autocomplete-wrapper {
  position: relative;
}

.autocomplete-results {
  position: absolute;
  z-index: 1000;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 0.25rem;
  padding: 0;
  list-style: none;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.125);
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
}

.autocomplete-results li {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f8f9fa;
  transition: all 0.2s ease;
}

.autocomplete-results li:last-child {
  border-bottom: none;
}

.autocomplete-results li:hover,
.autocomplete-results li.active {
  background-color: #f1f8ff;
}

.autocomplete-result {
  line-height: 1.4;
}

.progress {
  border-radius: 0.25rem;
  overflow: hidden;
}

.cursor-pointer {
  cursor: pointer;
}

.form-control-plaintext {
  padding: 0.375rem 0;
  border-bottom: 1px dashed #dee2e6;
}

/* Animación para las categorías */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 1000px;
}

/* Estilos para el sidebar */
.evaluation-sidebar {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 280px;
  background: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 0 8px 8px 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.evaluation-sidebar.sidebar-collapsed {
  transform: translateX(-90%) translateY(-50%);
}

.sidebar-toggle {
  position: absolute;
  right: -15px;
  top: 20px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: white;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1001;
}

.sidebar-content {
  padding: 15px;
  max-height: 70vh;
  overflow-y: auto;
}

.sidebar-header {
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.sidebar-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-category {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.sidebar-category:hover {
  background-color: #f8f9fa;
}

.sidebar-category.active {
  background-color: #e7f1ff;
  border-left-color: #0d6efd;
  font-weight: 500;
}

.sidebar-category.completed {
  background-color: #e8f5e9;
}

.sidebar-category.completed.active {
  background-color: #d4edda;
}

.sidebar-category small {
  background-color: #f1f8ff;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.75rem;
  color: #0d6efd;
}

.sidebar-category.completed small {
  background-color: #d4edda;
  color: #155724;
}

.floating-summary {
  position: fixed;
  bottom: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 600px;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px 8px 0 0;
  padding: 10px 15px;
  z-index: 1000;
  transition: all 0.3s ease;
}

.floating-summary.visible {
  bottom: 20px;
}

.summary-content {
  background: white;
  border-radius: 6px;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.category-section {
  scroll-margin-top: 20px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .btn-group-toggle label {
    min-width: 80px;
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
  }

  .card-header h3 {
    font-size: 1.1rem;
  }

  .evaluation-sidebar {
    width: 220px;
  }

  .evaluation-sidebar.sidebar-collapsed {
    transform: translateX(-85%) translateY(-50%);
  }

  .floating-summary {
    width: 95%;
    padding: 8px 10px;
  }
}

@media (max-width: 576px) {
  .evaluation-sidebar {
    display: none;
    /* Ocultar sidebar en móviles muy pequeños */
  }

  .floating-summary {
    left: 2.5%;
    transform: none;
    width: 95%;
  }
}


/* Estilos para móvil */
@media (max-width: 768px) {
  .evaluation-sidebar {
    width: 60px;
    left: -60px;
    transition: all 0.3s ease;
  }
  
  .evaluation-sidebar.mobile-sidebar {
    left: 0;
  }
  
  .evaluation-sidebar.mobile-sidebar .sidebar-content {
    display: none;
    width: 280px;
    background: white;
    position: absolute;
    left: 60px;
    top: 0;
    box-shadow: 5px 0 15px rgba(0,0,0,0.1);
    border-radius: 0 8px 8px 0;
    height: 100%;
  }
  
  .evaluation-sidebar.mobile-sidebar:not(.sidebar-collapsed) .sidebar-content {
    display: block;
  }
  
  .mobile-sidebar-handle {
    display: none;
  }
  
  .evaluation-sidebar.mobile-sidebar .mobile-sidebar-handle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    position: absolute;
    right: -60px;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    border-radius: 0 8px 8px 0;
    box-shadow: 5px 0 15px rgba(0,0,0,0.1);
    cursor: pointer;
    z-index: -1;
  }
  
  .progress-indicator {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    transform: rotate(180deg);
    font-weight: bold;
    color: var(--bs-primary);
    padding: 10px 5px;
  }
  
  .evaluation-sidebar.mobile-sidebar.sidebar-collapsed {
    left: -60px;
  }
  
  .evaluation-sidebar.mobile-sidebar.sidebar-collapsed .mobile-sidebar-handle {
    right: -60px;
  }
  
  .sidebar-toggle {
    display: none;
  }
}
</style>