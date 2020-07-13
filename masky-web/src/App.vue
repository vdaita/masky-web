<template>
  <div id="app">
    <div class="columns">
      <div class="column">
            <h1 class="is-size-1">Masky</h1>
      </div>
      <div class="column">
                    <img width="10%" src="./assets/mask.png">
        </div>
      </div>

    <h5 class="is-size-4">Gentle reminder for people to wear a mask.</h5>

    <br>

    <div class="columns">
      <div class="column is-one-third">
        <div class="col-md-6">
                <h2>Current Camera</h2>
                <code v-if="device">{{ device.label }}</code>
                <div class="border">
                    <web-cam
                        ref="webcam"
                        :device-id="deviceId"
                        width="100%"
                        @started="onStarted"
                        @stopped="onStopped"
                        @error="onError"
                        @cameras="onCameras"
                        @camera-change="onCameraChange"
                    />
                </div>

                <div class="row">
                    <div class="col-md-12">
                        <select v-model="camera">
                            <option>-- Select Device --</option>
                            <option
                                v-for="device in devices"
                                :key="device.deviceId"
                                :value="device.deviceId"
                            >{{ device.label }}</option>
                        </select>
                    </div>
                    <div class="col-md-12">
                        <!-- <button type="button" class="btn btn-primary" @click="onCapture">Capture Photo</button> -->
                        <b-button type="button" class="btn btn-danger" @click="onStop">Stop Camera</b-button>
                        <b-button type="button" class="btn btn-success" @click="onStart">Start Camera</b-button>
                    </div>
                </div>
            </div>
            <div class="field">
            <b-switch v-model="blurSwitch">
                Blur Faces
            </b-switch>
        </div>
      </div>
      <div class="column">
        <h4> The following people need to wear a mask: </h4>
        <img :key="image" v-for="image in images" v-bind:src="'data:image/jpeg;base64,' + image">
      </div>
    </div>
    
            <!-- <div class="col-md-6">
                <h2>Captured Image</h2>
                <figure class="figure">
                    <img :src="img" class="img-responsive" />
                </figure>
            </div> -->
    
    
    
    
  </div>
</template>

<script>
import axios from 'axios'
import {WebCam} from "vue-web-cam"

export default {
  name: "App",
  components: {
    WebCam
  },
  data() {
    return {
      images: [],
      currImage: "",
      img: null,
      camera: null,
      deviceId: null,
      devices: [],
      dont: true,
      blurSwitch: false
    };
  },
  mounted() {
    this.video = this.$refs.video;
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            this.video.src = URL.createObjectURL(stream);
            this.video.play();
        });
    }
  },
  computed: {
        device: function() {
            return this.devices.find(n => n.deviceId === this.deviceId);
        }
        
    },
  watch: {
        camera: function(id) {
            this.deviceId = id;
        },
        devices: function() {
            // Once we have a list select the first one
            const [first, ...tail] = this.devices;
            console.log(tail)
            if (first) {
                this.camera = first.deviceId;
                this.deviceId = first.deviceId;
            }
        },
        // images: function() {
        //   if(this.dont){
        //     this.images = []
        //   }
        // }
    },
  created() {
    this.currImage = setInterval(() => this.getPhoto(), 750);
    this.dont = false;
  },
  methods: {
    processData(base64input) {
      var myObj = {img: base64input, blur: this.blurSwitch}
      axios.post('http://127.0.0.1:5000/detect', {
        jsonData: JSON.stringify(myObj)
      })
      .then((response) => this.handleResponse(response))
    },
    handleResponse(response){
      if(!this.dont){
        this.images = response.data.split(",")
      }
    },
    getPhoto() {
      this.img = this.$refs.webcam.capture();
      // this.canvas = this.$refs.canvas;
      // this.canvas.getContext("2d").drawImage(this.video, 0, 0, 640, 480);
      this.processData(this.img.split(",")[1]);
    },
    onCapture() {
            this.img = this.$refs.webcam.capture();
        },
        onStarted(stream) {
            console.log("On Started Event", stream);
        },
        onStopped(stream) {
            console.log("On Stopped Event", stream);
        },
        onStop() {
            this.$refs.webcam.stop();
            this.currImage = setInterval(() => this.getPhoto(), 300);
            this.images = [];
            this.dont = true;
        },
        onStart() {
            this.$refs.webcam.start();
            this.currImage = setInterval(() => this.getPhoto(), 300);
            this.dont = false;
            window.location.reload()
        },
        onError(error) {
            console.log("On Error Event", error);
        },
        onCameras(cameras) {
            this.devices = cameras;
            console.log("On Cameras Event", cameras);
        },
        onCameraChange(deviceId) {
            this.deviceId = deviceId;
            this.camera = deviceId;
            console.log("On Camera Change Event", deviceId);
        }
  }
};
</script>

<style>
#app {
  /* font-family: "Avenir", Helvetica, Arial, sans-serif; */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}
</style>
