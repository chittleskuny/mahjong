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
        <el-row><el-button id="player_1_fixed_tiles">{{ player_1_fixed_tiles }}</el-button></el-row>
        <el-row><div id="player_1_played_tiles"></div></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_2">
        <el-row><el-button id="player_2_id">{{ player_2_id }}</el-button></el-row>
        <el-row><el-button id="player_2_fixed_tiles">{{ player_2_fixed_tiles }}</el-button></el-row>
        <el-row><div id="player_2_played_tiles"></div></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_3">
        <el-row><el-button id="player_3_id">{{ player_3_id }}</el-button></el-row>
        <el-row><el-button id="player_3_fixed_tiles">{{ player_3_fixed_tiles }}</el-button></el-row>
        <el-row id="player_3_played_tiles"></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_4">
        <el-row><el-button id="player_4_id">{{ player_4_id }}</el-button></el-row>
        <el-row><el-button id="player_4_fixed_tiles">{{ player_4_fixed_tiles }}</el-button></el-row>
        <el-row id="player_4_played_tiles"></el-row>
      </div></el-col>
    </el-row>
    <el-row id="my_buttons">
      <el-button id="pong" type="warning" @click="pong()">碰</el-button>
      <el-button id="kong" type="warning" @click="kong()">杠</el-button>
      <el-button id="chew" type="warning" @click="chew()">吃</el-button>
      <el-button id="draw" type="primary" @click="draw()">摸</el-button>
      <el-button id="win" type="danger" @click="win()">和</el-button>
    </el-row>
    <el-row id="my_tiles">{{ my_tiles }}</el-row>
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
        this.player_1_id = res.data.players[0]
        this.player_2_id = res.data.players[1]
        this.player_3_id = res.data.players[2]
        this.player_4_id = res.data.players[3]

        this.player_1_fixed_tiles = Array(
          res.data.player_fixed_tiles.player_1.pong,
          res.data.player_fixed_tiles.player_1.exposed_kong,
          res.data.player_fixed_tiles.player_1.concealed_pong,
          res.data.player_fixed_tiles.player_1.chow,
        )
        this.player_2_fixed_tiles = Array(
          res.data.player_fixed_tiles.player_2.pong,
          res.data.player_fixed_tiles.player_2.exposed_kong,
          res.data.player_fixed_tiles.player_2.concealed_pong,
          res.data.player_fixed_tiles.player_2.chow,
        )
        this.player_3_fixed_tiles = Array(
          res.data.player_fixed_tiles.player_3.pong,
          res.data.player_fixed_tiles.player_3.exposed_kong,
          res.data.player_fixed_tiles.player_3.concealed_pong,
          res.data.player_fixed_tiles.player_3.chow,
        )
        this.player_4_fixed_tiles = Array(
          res.data.player_fixed_tiles.player_4.pong,
          res.data.player_fixed_tiles.player_4.exposed_kong,
          res.data.player_fixed_tiles.player_4.concealed_pong,
          res.data.player_fixed_tiles.player_4.chow,
        )

        var data = res.data.player_played_tiles.player_1
        var player_1_played_tiles = document.getElementById('player_1_played_tiles')
        for(var i = 0; i < data.length; i++) {
          var button = document.createElement('button')
          button.setAttribute('class', 'el-button el-button--default')
          button.appendChild(document.createTextNode(data[i]))
          player_1_played_tiles.appendChild(button)
        }
        var data = res.data.player_played_tiles.player_2
        var player_2_played_tiles = document.getElementById('player_2_played_tiles')
        for(var i = 0; i < data.length; i++) {
          var button = document.createElement('button')
          button.setAttribute('class', 'el-button el-button--default')
          button.appendChild(document.createTextNode(data[i]))
          player_2_played_tiles.appendChild(button)
        }
        var data = res.data.player_played_tiles.player_3
        var player_3_played_tiles = document.getElementById('player_3_played_tiles')
        for(var i = 0; i < data.length; i++) {
          var button = document.createElement('button')
          button.setAttribute('class', 'el-button el-button--default')
          button.appendChild(document.createTextNode(data[i]))
          player_3_played_tiles.appendChild(button)
        }
        var data = res.data.player_played_tiles.player_4
        var player_4_played_tiles = document.getElementById('player_4_played_tiles')
        for(var i = 0; i < data.length; i++) {
          var button = document.createElement('button')
          button.setAttribute('class', 'el-button el-button--default')
          button.appendChild(document.createTextNode(data[i]))
          player_4_played_tiles.appendChild(button)
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
    },
    kong() {
    },
    chew() {
    },
    draw() {
    },
    win() {
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
