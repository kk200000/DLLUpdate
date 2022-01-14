import Home from '../components/Confirm.vue'

const routers = [
  {
    path: '/home',
    name: 'home',
    component: Home
  },
  {
    path: '/',
    component: Home
  },

];
export default {
  routers
};