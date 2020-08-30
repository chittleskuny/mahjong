<template>
  <div class="hello">
    <el-input v-model="input" placeholder="请输入您的 ID "></el-input>
    <el-button id="login" type="success" @click="login()">登录</el-button>
  </div>
</template>

<script>
import axios from 'axios'
import qs from 'qs'

export default {
  name: 'Hello',
  data() {
    return {
      input: ''
    }
  },
  methods: {
    login() {
      let data = { 'id': this.input }
      axios
        .post('/login', qs.stringify(data))
        .then(res => {
          localStorage["id"] = this.input
          this.board = res.data.board
          this.$router.push('/board')
        })
        .catch(error => {
            console.error(error)
        })
    }
  },
  created() {
    this.getMsg()
  }
}
</script>
