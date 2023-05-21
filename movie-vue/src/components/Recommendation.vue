<template>
  <div class="container mt-5 d-flex justify-content-center align-items-center">
    <div class="">
      <div>
        <h3>Recommendation</h3>
      </div>
      <form @submit.prevent="getRecommendation">
        <div class="rounded border p-4 list my-2">
          <div v-if="!isLoggedIn">
            <p>Якщо ви хочете отримати рекомендації на основі ваших переглядів,
              то вам потрібно увійти в свій аккаунт або зареєструватись</p>
            <LoginUser/>
          </div>
          <div v-else>
            <p>Ось твій список переглянутих фільмів</p>
            <ul>
              <li v-for="movie in listMovie" :key="movie">{{ movie }}</li>
            </ul>
            <div>
              <input class="form-control my-2" type="text" v-model="movieAdd.movie" placeholder="Додай назву фільму">
              <div class="">
              </div>
              <div class="d-flex justify-content-between">
                <button class="btn btn-danger" @click="logout_user">Вийти</button>
                <button class="btn btn-dark" @click="addMovie" type="button">Додати фільм</button>
              </div>
            </div>
          </div>
        </div>
        <div class="my-2">
          <label for="genre">Вибери жанр</label>
          <select class="form-select" v-model="selectGenre">
            <option value="">Відсутній</option>
            <option id="genre" v-for="genre in genres" :value="genre" :key="genre">{{ genre }}</option>
          </select>
        </div>
        <div class="my-2">
          <label>Рейтинг</label>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" value="false" v-model="selectRating">
            <label class="form-check-label" for="flexCheckDefault">
              Рейтинг від 7.0
            </label>
          </div>
        </div>
        <div class="d-flex justify-content-end my-3">
          <button type="submit" class="btn btn-dark">Шукати</button>
        </div>
      </form>
      <div class="list border rounded p-4 my-2" v-if="recommendations.length !== 0">
        <ul>
          <li v-for="rec in recommendations" :key="rec">{{ rec }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import {sendRequest} from "@/request";
import LoginUser from "@/components/Login.vue";
import {mapMutations, mapState} from "vuex";


export default {
  name: "RecommendationFilm",
  components: {LoginUser},
  computed: {
    ...mapState(['isLoggedIn']),
  },
  data() {
    return {
      genres: ['Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy', 'Romance', 'Sci-Fi', 'Family', 'Horror', 'Mystery', 'Thriller',
        'Animation', 'Crime', 'Documentary', 'Historical', 'Musical', 'Western', 'War'],
      selectGenre: '',
      selectRating: true,
      listMovie: [],
      movieAdd: {
        movie: ''
      },
      isAuthorized: !!localStorage.getItem('AccessToken'),
      recommendations: []
    }
  },
  mounted() {
    this.getListMovie()
  },
  watch:{
    isLoggedIn:{
      immediate: true,
      handler(newValue, oldValue){
        if (newValue !== oldValue){
          console.log("1")
          this.getListMovie();
        }
      }
    }
  },
  methods: {
    logout_user(){
      this.logout();
      this.listMovie, this.recommendations = [], [];
    },
    async getListMovie() {
      try {
        console.log("2")
        const response = await sendRequest('/movie', 'GET', null)
        if (response.ok) {
          const data = await response.json()
          this.listMovie = data['movies']
          console.log(this.listMovie)
        } else if (response.status === 403) {
          console.log('not Unauthorized')
        }
      } catch (e) {
        console.log(e)
      }
    },
    async addMovie() {
      try {
        const response = await sendRequest('/add_movie', 'POST', this.movieAdd)
        if (response.ok) {
          const data = await response.json()
          await this.getListMovie();
          this.movieAdd = ''
          console.log(data['message'])
        }
      } catch (e) {
        console.log(e)
      }
    },
    async getRecommendation() {
      if (this.listMovie){
        const info = {
          'user_movie': this.listMovie,
          'genre': this.selectGenre,
          'rating': this.selectRating
        }
        try {
          const response = await sendRequest('/recommendations', 'POST', info);
          if (response.ok) {
            const data = await response.json()
            this.recommendations = data['recommendations']
            this.$router.push('/')
            console.log(data)
          }
        } catch (e) {
          console.log(e)
        }
        console.log(info)
      }
    },
    ...mapMutations(['logout'])
  },
}
</script>

<style scoped>
.list {
  width: 500px;
  /*height: 200px;*/
}
</style>