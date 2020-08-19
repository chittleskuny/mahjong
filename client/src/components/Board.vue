<template>
  <div id="board"></div>
</template>

<script>
import axios from 'axios'
import qs from 'qs'

export default {
  name: 'Board',
  data() {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  },
  methods: {
    getBoard() {
      let data = { 'id': '1' }
      axios
      .post('/board', qs.stringify(data))
      .then(res => {
        this.players = res.data.players
        var board = document.getElementById('board')
        for(var i = 0; i < this.players.length; i++) {
          var button = document.createElement('button')
          button.setAttribute('class', 'el-button el-button--default')
          button.appendChild(document.createTextNode(this.players[i]))
          board.appendChild(button)
        }
      })
      .catch(error => {
          console.error(error)
      })
    }
  },
  created() {
    this.getBoard()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
