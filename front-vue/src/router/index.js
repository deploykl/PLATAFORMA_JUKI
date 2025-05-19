import { createRouter, createWebHistory  } from "vue-router";
import FormView from "@/views/FormView.vue";
import GraficoView from "@/views/GraficoView.vue";

const routes = [
  {
    path: "/",
    name: "Form",
    component: FormView,
  },
   {
    path: "/grafico",
    name: "Grafico",
    component: GraficoView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
