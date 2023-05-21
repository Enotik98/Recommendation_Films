import { createApp } from 'vue'
import {createWebHistory, createRouter} from "vue-router";
import App from './App.vue'
import Login from "@/components/Login.vue";
import "bootstrap/dist/css/bootstrap.css"
import "bootstrap/dist/js/bootstrap";
import "jquery/dist/jquery"
import Recommendation from "@/components/Recommendation.vue";
import Registration from "@/components/Registration.vue";
import store from "@/store";

const routes = [
    {
        path: '/login',
        component:Login
    },
    {
        path: '/',
        component: Recommendation
    },
    {
        path: '/registration',
        component: Registration
    }
]
const router = createRouter({
    history: createWebHistory(),
    routes
});
const  app =createApp(App)
app.use(router)
app.use(store)
app.mount('#app')
// createApp(App).mount('#app')
