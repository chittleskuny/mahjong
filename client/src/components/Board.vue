<template>
  <div id="board">
    <el-row id="number_total">number: {{ number }}/{{ total }}</el-row>
    <el-row id="len_card_pile">len_card_pile: {{ len_card_pile }}</el-row>
    <el-row id="banker">banker: player_{{ banker }}</el-row>
    <el-row id="turn">turn: player_{{ turn }}</el-row>
    <el-row id="common_buttons">
      <el-button id="start" @click="startBoard()">START</el-button>
      <el-button id="restart" @click="restartBoard()">RESTART</el-button>
      <el-button id="join" @click="joinBoard()">JOIN</el-button>
    </el-row>
    <el-row>
      <el-col :span="6"><div id="player_1">
        <el-row><el-button id="player_1_id">{{ player_1_id }}</el-button></el-row>
        <el-row><div id="player_1_fixed_tiles"></div></el-row>
        <el-row><div id="player_1_played_tiles"></div></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_2">
        <el-row><el-button id="player_2_id">{{ player_2_id }}</el-button></el-row>
        <el-row><div id="player_2_fixed_tiles"></div></el-row>
        <el-row><div id="player_2_played_tiles"></div></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_3">
        <el-row><el-button id="player_3_id">{{ player_3_id }}</el-button></el-row>
        <el-row><div id="player_3_fixed_tiles"></div></el-row>
        <el-row id="player_3_played_tiles"></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_4">
        <el-row><el-button id="player_4_id">{{ player_4_id }}</el-button></el-row>
        <el-row><div id="player_4_fixed_tiles"></div></el-row>
        <el-row id="player_4_played_tiles"></el-row>
      </div></el-col>
    </el-row>
    <el-row id="my_tiles">{{ my_tiles }}</el-row>
    <el-row id="my_buttons">
      <el-button id="pong" type="warning" @click="pong()">碰</el-button>
      <el-button id="kong" type="warning" @click="kong()">杠</el-button>
      <el-button id="chow" type="warning" @click="chow()">吃</el-button>
    </el-row>
    <el-row id="my_buttons">
      <el-button id="win" type="danger" @click="win()">和</el-button>
      <el-button id="draw" type="primary" @click="draw()">摸</el-button>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import qs from 'qs'


function play(tile) {
  let data = { 'id': '1', 'player': localStorage['id'], 'tile': tile }
  axios
  .post('/board/play', qs.stringify(data))
  .then(res => {
    location.reload()
  })
  .catch(error => {
    console.error(error)
  })
}


export default {
  name: 'Board',
  data() {
    return {
      total: '',
      number: '',
      len_card_pile: '',
      banker: '',
      turn: '',
      player_1_id: '',
      player_2_id: '',
      player_3_id: '',
      player_4_id: '',
      player_1_fixed_tiles: '',
      player_2_fixed_tiles: '',
      player_3_fixed_tiles: '',
      player_4_fixed_tiles: '',
      my_tiles: '',
    }
  },
  methods: {
    getBoard() {
      let data = { 'id': '1', 'player': localStorage['id'] }
      axios
      .post('/board', qs.stringify(data))
      .then(res => {
        console.log(res.data)
        this.total = res.data.total
        this.number = res.data.number
        this.len_card_pile = res.data.len_card_pile
        this.banker = res.data.banker
        this.turn = res.data.turn

        var players = { 'player_1': 0, 'player_2': 1, 'player_3': 2, 'player_4': 3 }
        for (var player in players) {
          this[player + '_id'] = res.data.players[players[player]]

          var data = res.data.player_fixed_tiles[player]
          var played_tiles = document.getElementById(player + '_fixed_tiles')
          for(var i = 0; i < data.flower.length; i++) {
            var button = document.createElement('button')
            button.setAttribute('class', 'el-button el-button--info')
            button.appendChild(document.createTextNode(data.flower[i]))
            played_tiles.appendChild(button)
          }
          for(var i = 0; i < data.pong.length; i++) {
            var button = document.createElement('button')
            button.setAttribute('class', 'el-button el-button--info')
            button.appendChild(document.createTextNode(data.pong[i]))
            played_tiles.appendChild(button)
          }
          for(var i = 0; i < data.exposed_kong.length; i++) {
            var button = document.createElement('button')
            button.setAttribute('class', 'el-button el-button--info')
            button.appendChild(document.createTextNode(data.exposed_kong[i]))
            played_tiles.appendChild(button)
          }
          for(var i = 0; i < data.concealed_kong.length; i++) {
            var button = document.createElement('button')
            button.setAttribute('class', 'el-button el-button--info')
            button.appendChild(document.createTextNode(data.concealed_kong[i]))
            played_tiles.appendChild(button)
          }
          for(var i = 0; i < data.chow.length; i++) {
            var button = document.createElement('button')
            button.setAttribute('class', 'el-button el-button--info')
            button.appendChild(document.createTextNode(data.chow[i]))
            played_tiles.appendChild(button)
          }

          var data = res.data.player_played_tiles[player]
          var played_tiles = document.getElementById(player + '_played_tiles')
          for(var i = 0; i < data.length; i++) {
            var button = document.createElement('button')
            button.setAttribute('class', 'el-button el-button--default')
            button.appendChild(document.createTextNode(data[i]))
            played_tiles.appendChild(button)
          }
        }

        var data = res.data.my_tiles
        var my_tiles = document.getElementById('my_tiles')
        for(var i = 0; i < data.length; i++) {
          var button = document.createElement('button')
          button.setAttribute('class', 'el-button el-button--success')
          button.appendChild(document.createTextNode(data[i]))
          button.onclick = function() { return play(this.innerHTML) }
          my_tiles.appendChild(button)
        }
      })
      .catch(error => {
        console.error(error)
      })
    },
    startBoard() {
      let data = { 'id': '1' }
      axios
      .post('/board/start', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
    restartBoard() {
      let data = { 'id': '1' }
      axios
      .post('/board/restart', qs.stringify(data))
      .then(res => {
        this.$router.go(0)
      })
      .catch(error => {
        console.error(error)
      })
    },
    joinBoard() {
      let data = { 'id': '1', 'slave': localStorage['id'] }
      axios
      .post('/board/join', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
    pong() {
      let data = { 'id': '1', 'slave': localStorage['id'] }
      axios
      .post('/board/pong', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
    kong() {
      let data = { 'id': '1', 'player': localStorage['id'] }
      axios
      .post('/board/kong', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
    chow() {
      let data = { 'id': '1', 'player': localStorage['id'] }
      axios
      .post('/board/chow', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
    draw() {
      let data = { 'id': '1', 'player': localStorage['id'] }
      axios
      .post('/board/draw', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
    win() {
      let data = { 'id': '1', 'player': localStorage['id'] }
      axios
      .post('/board/win', qs.stringify(data))
      .then(res => {
      })
      .catch(error => {
        console.error(error)
      })
    },
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
