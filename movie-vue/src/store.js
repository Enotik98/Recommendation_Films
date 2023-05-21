import {createStore} from 'vuex';
const store = createStore({
    state:{
        isLoggedIn: !!localStorage.getItem("AccessToken")
    },
    mutations:{
        login(state){
            state.isLoggedIn = !!localStorage.getItem("AccessToken");
        },
        logout(state){
            localStorage.removeItem("AccessToken");
            localStorage.removeItem("RefreshToken");
            state.isLoggedIn = false;
        }
    }
})
export default store