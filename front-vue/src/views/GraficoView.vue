<template>
  <div class="container py-3">
    <h2 class="mb-4 fw-bold">Puntuación por Categoría</h2>
    
    <!-- Filtros -->
    <div class="row mb-4">
      <div class="col-md-4">
        <label class="form-label">Seleccionar Ipress</label>
        <select class="form-select" v-model="selectedIpressId">
          <option value="">Todos</option>
          <option v-for="ipress in ipressList" :value="ipress.id" :key="ipress.id">
            {{ ipress.nombre }} ({{ ipress.codigo }})
          </option>
        </select>
      </div>
    </div>
    
    <!-- Tabla de resultados -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Resultados por Categoría</h5>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Categoría</th>
                <th>Preguntas</th>
                <th>Puntaje Total</th>
                <th>Puntaje Máximo</th>
                <th>Porcentaje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cat in categoriasConPuntaje" :key="cat.id">
                <td>{{ cat.descripcion }}</td>
                <td>{{ cat.totalPreguntas }}</td>
                <td>{{ cat.puntajeTotal.toFixed(2) }}</td>
                <td>{{ cat.puntajeMaximo }}</td>
                <td>
                  <div class="progress">
                    <div class="progress-bar" 
                         :class="getProgressBarClass(cat.porcentaje)"
                         role="progressbar" 
                         :style="{width: cat.porcentaje + '%'}" 
                         :aria-valuenow="cat.porcentaje" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                      {{ cat.porcentaje.toFixed(1) }}%
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Gráfico de barras -->
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Distribución de Puntajes</h5>
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { Chart } from 'chart.js';

// Configuración de Axios
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/ficha/',
  timeout: 5000
});

// Datos reactivos
const categorias = ref([]);
const preguntas = ref([]);
const respuestas = ref([]);
const ipressList = ref([]);
const selectedIpressId = ref('');
const chartCanvas = ref(null);
let chartInstance = null;

// Obtener datos iniciales con relaciones incluidas
const fetchData = async () => {
  try {
    const [catRes, pregRes, respRes, ipressRes] = await Promise.all([
      api.get('categorias-pregunta/'),
      api.get('preguntas/?expand=categoria'), // Asegurar que viene la relación
      api.get('respuestas/?expand=pregunta,ipress'), // Asegurar relaciones
      api.get('ipress/')
    ]);
    
    categorias.value = catRes.data;
    preguntas.value = pregRes.data;
    respuestas.value = respRes.data;
    ipressList.value = ipressRes.data;
    
    console.log('Datos cargados:', {
      categorias: categorias.value,
      preguntas: preguntas.value,
      respuestas: respuestas.value
    });
  } catch (error) {
    console.error('Error al obtener datos:', error);
  }
};

// Calcular puntuaciones por categoría - VERSIÓN CORREGIDA
const categoriasConPuntaje = computed(() => {
  return categorias.value.map(categoria => {
    // Filtrar preguntas de esta categoría (comparación corregida)
    const preguntasCategoria = preguntas.value.filter(p => {
      // Manejar tanto si categoria es objeto o ID
      const catId = p.categoria?.id || p.categoria;
      return catId == categoria.id; // Usar == para comparación flexible
    });
    
    // Filtrar respuestas según filtros
    let respuestasFiltradas = respuestas.value;
    if (selectedIpressId.value) {
      respuestasFiltradas = respuestasFiltradas.filter(r => {
        const ipressId = r.ipress?.id || r.ipress;
        return ipressId == selectedIpressId.value;
      });
    }
    
    // Calcular puntajes
    let puntajeTotal = 0;
    let preguntasConRespuesta = 0;
    
    preguntasCategoria.forEach(pregunta => {
      const respuesta = respuestasFiltradas.find(r => {
        const preguntaId = r.pregunta?.id || r.pregunta;
        return preguntaId == pregunta.id;
      });
      
      if (respuesta) {
        puntajeTotal += parseFloat(respuesta.puntaje) || 0;
        preguntasConRespuesta++;
      }
    });
    
    // Calcular puntaje máximo (1 punto por pregunta)
    const puntajeMaximo = preguntasCategoria.length;
    const porcentaje = puntajeMaximo > 0 ? (puntajeTotal / puntajeMaximo) * 100 : 0;
    
    return {
      ...categoria,
      totalPreguntas: preguntasCategoria.length,
      preguntasConRespuesta,
      puntajeTotal,
      puntajeMaximo,
      porcentaje
    };
  });
});

// Clases para la barra de progreso
const getProgressBarClass = (porcentaje) => {
  if (porcentaje >= 75) return 'bg-success';
  if (porcentaje >= 50) return 'bg-info';
  if (porcentaje >= 25) return 'bg-warning';
  return 'bg-danger';
};

// Inicializar gráfico
// Inicializar gráfico
const initChart = () => {
  if (chartInstance) {
    chartInstance.destroy();
  }
  
  const ctx = chartCanvas.value.getContext('2d');
  const data = {
    labels: categoriasConPuntaje.value.map(c => c.descripcion),
    datasets: [{
      label: 'Porcentaje de cumplimiento',
      data: categoriasConPuntaje.value.map(c => c.porcentaje),
      backgroundColor: categoriasConPuntaje.value.map(c => 
        getBackgroundColor(c.porcentaje)) // Aquí faltaba el paréntesis de cierre
    }]
  };
  
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Porcentaje (%)'
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const cat = categoriasConPuntaje.value[context.dataIndex];
              return [
                `Puntaje: ${cat.puntajeTotal.toFixed(2)}/${cat.puntajeMaximo}`,
                `Preguntas: ${cat.preguntasConRespuesta}/${cat.totalPreguntas}`
              ];
            }
          }
        }
      }
    }
  });
};

// Colores para el gráfico
const getBackgroundColor = (porcentaje) => {
  if (porcentaje >= 75) return 'rgba(40, 167, 69, 0.7)';
  if (porcentaje >= 50) return 'rgba(23, 162, 184, 0.7)';
  if (porcentaje >= 25) return 'rgba(255, 193, 7, 0.7)';
  return 'rgba(220, 53, 69, 0.7)';
};

// Observar cambios para actualizar gráfico
watch(categoriasConPuntaje, () => {
  if (chartCanvas.value) {
    initChart();
  }
}, { deep: true });

// Ciclo de vida
onMounted(async () => {
  await fetchData();
  if (chartCanvas.value) {
    initChart();
  }
});

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  min-height: 400px;
  margin: 0 auto;
}

.card {
  margin-top: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.card-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.progress {
  height: 20px;
}

.table-responsive {
  max-height: 500px;
  overflow-y: auto;
}
</style>