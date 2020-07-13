import Vue from "vue";
import App from "./App.vue";
// import PhotoGrid from 'vue-photo-grid';
 
// Vue.use(PhotoGrid);
import Buefy from 'buefy'
import 'buefy/dist/buefy.css'

Vue.use(Buefy)

Vue.config.productionTip = false;

new Vue({
  render: h => h(App)
}).$mount("#app");
