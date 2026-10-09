const { createScopedThreejs } = require('threejs-miniprogram')

const RISK_COLOR = {
  low: 0x5fcf84,
  medium: 0xf4a940,
  high: 0xe24d4d
}

Component({
  properties: {
    riskLevel: {
      type: String,
      value: 'low'
    },
    heartRate: {
      type: Number,
      value: 72
    },
    coronaryHighlight: {
      type: Boolean,
      value: false
    },
    tachycardiaHighlight: {
      type: Boolean,
      value: false
    },
    recoveryProgress: {
      type: Number,
      value: 0
    },
    rhythmStability: {
      type: Number,
      value: 0.6
    }
  },

  lifetimes: {
    ready() {
      this.initThree()
    },
    detached() {
      this.disposeThree()
    }
  },

  observers: {
    'riskLevel, heartRate, coronaryHighlight, tachycardiaHighlight, recoveryProgress, rhythmStability': function () {
      this.applyRiskVisuals()
    }
  },

  methods: {
    initThree() {
      const query = wx.createSelectorQuery().in(this)
      query.select('#heartWebgl').fields({ node: true, size: true }).exec((res) => {
        const info = res && res[0]
        if (!info || !info.node) return

        const canvas = info.node
        const width = info.width || 300
        const height = info.height || 220
        const dpr = wx.getWindowInfo().pixelRatio || 2

        const THREE = createScopedThreejs(canvas)
        this.THREE = THREE

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true })
        renderer.setPixelRatio(dpr)
        renderer.setSize(width, height)

        const scene = new THREE.Scene()
        const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100)
        camera.position.set(0, 0, 6)

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.9)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
        directionalLight.position.set(3, 4, 5)
        scene.add(ambientLight)
        scene.add(directionalLight)

        const heartGroup = new THREE.Group()
        scene.add(heartGroup)

        const baseColor = RISK_COLOR[this.properties.riskLevel] || RISK_COLOR.low
        const leftVentricleMaterial = new THREE.MeshPhongMaterial({
          color: baseColor,
          shininess: 42,
          transparent: true,
          opacity: 0.95
        })

        const rightVentricleMaterial = new THREE.MeshPhongMaterial({
          color: baseColor,
          shininess: 40,
          transparent: true,
          opacity: 0.95
        })

        const leftAtriumMaterial = new THREE.MeshPhongMaterial({
          color: baseColor,
          shininess: 36,
          transparent: true,
          opacity: 0.92
        })

        const rightAtriumMaterial = new THREE.MeshPhongMaterial({
          color: baseColor,
          shininess: 34,
          transparent: true,
          opacity: 0.92
        })

        const leftVentricle = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 18), leftVentricleMaterial)
        leftVentricle.scale.set(0.8, 1.15, 0.8)
        leftVentricle.position.set(-0.52, -0.08, 0)

        const rightVentricle = new THREE.Mesh(new THREE.SphereGeometry(0.92, 18, 18), rightVentricleMaterial)
        rightVentricle.scale.set(0.76, 1.04, 0.76)
        rightVentricle.position.set(0.45, 0, 0.08)

        const leftAtrium = new THREE.Mesh(new THREE.SphereGeometry(0.45, 16, 16), leftAtriumMaterial)
        leftAtrium.position.set(-0.2, 0.9, -0.2)
        leftAtrium.scale.set(0.9, 0.75, 0.85)

        const rightAtrium = new THREE.Mesh(new THREE.SphereGeometry(0.4, 16, 16), rightAtriumMaterial)
        rightAtrium.position.set(0.45, 0.8, 0)
        rightAtrium.scale.set(0.9, 0.7, 0.8)

        const coronaryMaterial = new THREE.MeshPhongMaterial({
          color: 0xc73737,
          emissive: 0x3a1111,
          shininess: 50,
          transparent: true,
          opacity: 0.75
        })
        const coronaryRing = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.06, 12, 50), coronaryMaterial)
        coronaryRing.rotation.x = 1.3
        coronaryRing.position.set(0, 0.05, 0.4)

        heartGroup.add(leftVentricle)
        heartGroup.add(rightVentricle)
        heartGroup.add(leftAtrium)
        heartGroup.add(rightAtrium)
        heartGroup.add(coronaryRing)

        heartGroup.rotation.x = -0.2
        heartGroup.rotation.y = 0.5

        this.renderer = renderer
        this.scene = scene
        this.camera = camera
        this.canvas = canvas
        this.heartGroup = heartGroup
        this.leftVentricleMaterial = leftVentricleMaterial
        this.rightVentricleMaterial = rightVentricleMaterial
        this.leftAtriumMaterial = leftAtriumMaterial
        this.rightAtriumMaterial = rightAtriumMaterial
        this.coronaryMaterial = coronaryMaterial
        this.leftVentricle = leftVentricle
        this.rightVentricle = rightVentricle
        this.leftAtrium = leftAtrium
        this.rightAtrium = rightAtrium
        this.coronaryRing = coronaryRing
        this.baseRotationX = heartGroup.rotation.x
        this.baseRotationY = heartGroup.rotation.y
        this.autoRotate = 0.004

        this.applyRiskVisuals()
        this.startAnimateLoop()
      })
    },

    applyRiskVisuals() {
      if (!this.leftVentricleMaterial || !this.rightVentricleMaterial || !this.leftAtriumMaterial || !this.rightAtriumMaterial || !this.coronaryMaterial) return
      const level = this.properties.riskLevel || 'low'
      const color = RISK_COLOR[level] || RISK_COLOR.low
      const recoveryProgress = Math.max(0, Math.min(1, Number(this.properties.recoveryProgress) || 0))

      let bodyColorHex = color
      if (this.THREE) {
        const bodyColor = new this.THREE.Color(color)
        const targetGreen = new this.THREE.Color(0x35c86b)
        bodyColor.lerp(targetGreen, recoveryProgress)
        bodyColorHex = bodyColor.getHex()
      }

      this.leftVentricleMaterial.color.setHex(bodyColorHex)
      this.rightVentricleMaterial.color.setHex(bodyColorHex)
      this.leftAtriumMaterial.color.setHex(bodyColorHex)
      this.rightAtriumMaterial.color.setHex(bodyColorHex)

      if (this.properties.tachycardiaHighlight) {
        this.leftVentricleMaterial.emissive.setHex(0x6e2020)
        this.rightVentricleMaterial.emissive.setHex(0x6e2020)
      } else {
        this.leftVentricleMaterial.emissive.setHex(0x1a0909)
        this.rightVentricleMaterial.emissive.setHex(0x1a0909)
      }

      if (level === 'high' || this.properties.coronaryHighlight) {
        this.coronaryMaterial.opacity = 1
        this.coronaryMaterial.color.setHex(0xff2b2b)
        this.coronaryMaterial.emissive.setHex(0x882222)
      } else if (level === 'medium') {
        this.coronaryMaterial.opacity = 0.9
        this.coronaryMaterial.color.setHex(0xd84e4e)
        this.coronaryMaterial.emissive.setHex(0x552222)
      } else {
        this.coronaryMaterial.opacity = 0.65
        this.coronaryMaterial.color.setHex(0xc73737)
        this.coronaryMaterial.emissive.setHex(0x2d1414)
      }

      this.isHighRisk = level === 'high'
    },

    startAnimateLoop() {
      if (!this.renderer || !this.scene || !this.camera || !this.heartGroup) return
      const startTime = Date.now()

      const render = () => {
        if (!this.renderer) return
        const bpm = Number(this.properties.heartRate) || 72
        const stability = Math.max(0, Math.min(1, Number(this.properties.rhythmStability) || 0.6))
        const pulse = Math.max(0.04, Math.min(0.16, bpm / 1000))
        const t = (Date.now() - startTime) / 1000
        const phaseNoise = (1 - stability) * 0.18 * Math.sin(t * 5.3)
        const phase = t * (bpm / 60) * Math.PI * 2 + phaseNoise
        const scale = 1 + Math.sin(phase) * pulse

        this.heartGroup.scale.set(scale, scale, scale)
        this.heartGroup.rotation.y += this.autoRotate

        if (this.isHighRisk) {
          const jitter = Math.sin(t * 26) * 0.022
          const randomShake = (Math.random() - 0.5) * 0.02
          this.heartGroup.rotation.x = this.baseRotationX + jitter + randomShake
          this.heartGroup.rotation.y += Math.sin(t * 24) * 0.006

          const flicker = 0.4 + Math.abs(Math.sin(t * 20)) * 0.6
          this.coronaryMaterial.emissiveIntensity = flicker
          this.leftVentricleMaterial.emissiveIntensity = 0.25 + flicker * 0.35
          this.rightVentricleMaterial.emissiveIntensity = 0.25 + flicker * 0.35
        } else {
          this.heartGroup.rotation.x = this.baseRotationX + (1 - stability) * 0.014 * Math.sin(t * 8)
          this.coronaryMaterial.emissiveIntensity = 0.65
          this.leftVentricleMaterial.emissiveIntensity = 0.2
          this.rightVentricleMaterial.emissiveIntensity = 0.2
        }

        this.renderer.render(this.scene, this.camera)
        if (this.canvas && this.canvas.requestAnimationFrame) {
          this.frameHandle = this.canvas.requestAnimationFrame(render)
        }
      }

      if (this.canvas && this.canvas.requestAnimationFrame) {
        this.frameHandle = this.canvas.requestAnimationFrame(render)
      }
    },

    onTouchStart(e) {
      const touches = e.touches || []
      this.touchCache = touches
      if (touches.length === 1) {
        this.lastX = touches[0].x
      }
      if (touches.length === 2) {
        this.lastDistance = this.getDistance(touches[0], touches[1])
      }
    },

    onTouchMove(e) {
      if (!this.heartGroup || !this.camera) return
      const touches = e.touches || []
      if (touches.length === 1 && typeof this.lastX === 'number') {
        const deltaX = touches[0].x - this.lastX
        this.heartGroup.rotation.y += deltaX * 0.01
        this.lastX = touches[0].x
      }
      if (touches.length === 2 && typeof this.lastDistance === 'number') {
        const currentDistance = this.getDistance(touches[0], touches[1])
        const delta = currentDistance - this.lastDistance
        this.camera.position.z = Math.max(4, Math.min(8, this.camera.position.z - delta * 0.01))
        this.lastDistance = currentDistance
      }
    },

    onTouchEnd() {
      this.lastX = null
      this.lastDistance = null
    },

    getDistance(p1, p2) {
      const dx = p1.x - p2.x
      const dy = p1.y - p2.y
      return Math.sqrt(dx * dx + dy * dy)
    },

    disposeThree() {
      if (this.canvas && this.canvas.cancelAnimationFrame && this.frameHandle) {
        this.canvas.cancelAnimationFrame(this.frameHandle)
      }
      this.frameHandle = null
      if (this.renderer) {
        this.renderer.dispose()
      }
      this.renderer = null
      this.scene = null
      this.camera = null
      this.heartGroup = null
      this.leftVentricleMaterial = null
      this.rightVentricleMaterial = null
      this.leftAtriumMaterial = null
      this.rightAtriumMaterial = null
      this.coronaryMaterial = null
      this.leftVentricle = null
      this.rightVentricle = null
      this.leftAtrium = null
      this.rightAtrium = null
      this.coronaryRing = null
    }
  }
})
