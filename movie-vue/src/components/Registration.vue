<template>
  <div class="container mt-5">
    <div class="d-flex justify-content-center align-items-center">
      <form class="border rounded p-4 " @submit.prevent="registration">
        <h2 class="d-flex justify-content-center">Registration</h2>
        <div class="my-2">
          <label>Username</label>
          <input type="text" class="form-control" v-model="formData.username">
        </div>
        <div class="my-2">
          <label>Password</label>
          <input type="password" class="form-control" v-model="formData.password">
        </div>
        <div class="d-flex justify-content-between mt-2">
          <router-link to="/" class="btn btn-outline-dark">Login</router-link>
          <button type="submit" class="btn btn-dark">Registration</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import {sendRequest} from "@/request";

export default {
  name: "RegistrationUser",
  data() {
    return {
      formData: {
        username: '',
        password: '',
      }
    }
  },
  methods: {
    async registration() {
      try {
        const response = await sendRequest('/registration', 'POST', this.formData)
        if (response.ok) {
          const data = await response.json()
          console.log(data['message'])
        }
      } catch (e) {
        console.log(e)
      }
    }
  }
}
</script>

<style scoped>
form {
  width: 350px;
}
</style>