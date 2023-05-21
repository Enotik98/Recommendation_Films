<template>
  <div class=" mt-2">
    <!--    <div class="d-flex justify-content-center align-items-center">-->
    <form class=" " @submit.prevent="loginUser">
      <h2 class="d-flex justify-content-center">Login</h2>
      <div class="my-2">
        <label>Username</label>
        <input type="text" class="form-control" v-model="formData.username">
      </div>
      <div class="my-2">
        <label>Password</label>
        <input type="password" class="form-control" v-model="formData.password">
      </div>
      <div class="d-flex justify-content-between mt-2">
        <router-link to="/registration" class="btn btn-outline-dark">Registration</router-link>
        <button type="submit" class="btn btn-dark">Login</button>
      </div>
    </form>
    <!--    </div>-->
  </div>
</template>

<script>
import {sendRequest} from "@/request";
import {mapMutations} from "vuex";

export default {
  name: "LoginUser",
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      changeBtn: false
    }
  },
  methods: {
    async loginUser() {
      try {
        const response = await sendRequest('/login', 'POST', this.formData)
        if (response.ok) {
          const data = await response.json()
          if (data['message']) {
            console.log(data['message'])
          }else {
            localStorage.setItem('AccessToken', data['accessToken'])
            localStorage.setItem('RefreshToken', data['refreshToken'])
            this.login()
          }
        } else {
          console.log("error")
        }
      } catch (e) {
        console.log(e)
      }
    },
    ...mapMutations(['login'])
  }
}
</script>

<style scoped>

</style>