<template>
  <div id="board">
    <el-row id="number_total">number: {{ number }}/{{ total }}</el-row>
    <el-row id="len_card_pile">len_card_pile: {{ len_card_pile }}</el-row>
    <el-row id="banker">banker: player_{{ banker }}</el-row>
    <el-row id="turn">turn: player_{{ turn }}</el-row>
    <el-row>
      <el-col :span="6"><div id="player_1">
        <el-row><el-button id="player_1_id">{{ player_1_id }}</el-button></el-row>
        <el-row><el-button id="player_1_fixed_tiles">{{ player_1_fixed_tiles }}</el-button></el-row>
        <el-row><el-button id="player_1_played_tiles">{{ player_1_played_tiles }}</el-button></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_2">
        <el-row><el-button id="player_2_id">{{ player_2_id }}</el-button></el-row>
        <el-row><el-button id="player_2_fixed_tiles">{{ player_2_fixed_tiles }}</el-button></el-row>
        <el-row><el-button id="player_2_played_tiles">{{ player_2_played_tiles }}</el-button></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_3">
        <el-row><el-button id="player_3_id">{{ player_3_id }}</el-button></el-row>
        <el-row><el-button id="player_3_fixed_tiles">{{ player_3_fixed_tiles }}</el-button></el-row>
        <el-row><el-button id="player_3_played_tiles">{{ player_3_played_tiles }}</el-button></el-row>
      </div></el-col>
      <el-col :span="6"><div id="player_4">
        <el-row><el-button id="player_4_id">{{ player_4_id }}</el-button></el-row>
        <el-row><el-button id="player_4_fixed_tiles">{{ player_4_fixed_tiles }}</el-button></el-row>
        <el-row><el-button id="player_4_played_tiles">{{ player_4_played_tiles }}</el-button></el-row>
      </div></el-col>
    </el-row>
    <el-row id="my_tiles">{{ my_tiles }}</el-row>
  </div>
</template>

<script>
import axios from 'axios'
import qs from 'qs'

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
      player_1_played_tiles: '',
      player_2_played_tiles: '',
      player_3_played_tiles: '',
      player_4_played_tiles: '',
      my_tiles: '',
    }
  },
  methods: {
    getBoard() {
      let data = { 'id': '1' }
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
        this.player_1_fixed_tiles = res.data.player_fixed_tiles.player_1.toString()
        this.player_2_fixed_tiles = res.data.player_fixed_tiles.player_2.toString()
        this.player_3_fixed_tiles = res.data.player_fixed_tiles.player_3.toString()
        this.player_4_fixed_tiles = res.data.player_fixed_tiles.player_4.toString()
        this.player_1_played_tiles = res.data.player_played_tiles.player_1.toString()
        this.player_2_played_tiles = res.data.player_played_tiles.player_2.toString()
        this.player_3_played_tiles = res.data.player_played_tiles.player_3.toString()
        this.player_4_played_tiles = res.data.player_played_tiles.player_4.toString()
        this.my_tiles = res.data.my_tiles.toString()
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
