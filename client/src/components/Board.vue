<template>
  <div id="board"></div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Board',
  data() {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  },
  methods: {
    getBoard() {
      axios
      .get('/board')
      .then(res => {
        this.len_card_pile = res.data.len_card_pile
        this.discard_pile = res.data.discard_pile
        this.players = res.data.players
        this.player_tiles = res.data.player_tiles
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
