let video, videoTexture, poseDetector, bodySegmenter, scene, camera, renderer;
let curr = null;
let isLoaded = false;
let bodyPoints = {};

const garments = {
    shirt: {
        anchors: [
            { name: 'leftShoulder', position: [0.2, 0.1] },
            { name: 'rightShoulder', position: [0.8, 0.1] },
            { name: 'leftHip', position: [0.2, 0.7] },
            { name: 'rightHip', position: [0.8, 0.7] }
        ],
        color: 0xff0000,
        opacity: 0.8
    },
    dress: {
        anchors: [
            { name: 'leftShoulder', position: [0.2, 0.1] },
            { name: 'rightShoulder', position: [0.8, 0.1] },
            { name: 'leftKnee', position: [0.2, 0.8] },
            { name: 'rightKnee', position: [0.8, 0.8] }
        ],
        color: 0x00ff00,
        opacity: 0.8
    },
    jacket: {
        anchors: [
            { name: 'leftShoulder', position: [0.2, 0.1] },
            { name: 'rightShoulder', position: [0.8, 0.1] },
            { name: 'leftElbow', position: [0.15, 0.4] },
            { name: 'rightElbow', position: [0.85, 0.4] },
            { name: 'leftHip', position: [0.2, 0.7] },
            { name: 'rightHip', position: [0.8, 0.7] }
        ],
        color: 0x0000ff,
        opacity: 0.8
    },
    pant: {
        anchors: [
            { name: 'leftHip', position: [0.2, 0.7] },
            { name: 'rightHip', position: [0.8, 0.7] },
            { name: 'leftKnee', position: [0.2, 0.85] },
            { name: 'rightKnee', position: [0.8, 0.85] },
            { name: 'leftAnkle', position: [0.2, 1.0] },
            { name: 'rightAnkle', position: [0.8, 1.0] }
        ],
        color: 0x964B00, // brownish color
        opacity: 0.8
    },
    skirt: {
        anchors: [
            { name: 'leftHip', position: [0.2, 0.7] },
            { name: 'rightHip', position: [0.8, 0.7] },
            { name: 'leftKnee', position: [0.2, 0.85] },
            { name: 'rightKnee', position: [0.8, 0.85] }
        ],
        color: 0xff69b4, // pinkish color
        opacity: 0.8
    }
};

// Three.js
function initThreeJs()
{
    scene = new THREE.Scene();
    // Setting up the camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    // WebGL Renderer
    renderer = new THREE.WebGLRenderer(
        {
            canvas: document.getElementById('arCanvas'),
            alpha: true,
            antialias: true
        }
    );
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
}

// Starting Webcam
async function setupWebcam()
{
    video = document.createElement('video');
    video.autoplay = true;
    video.playsInline = true;

    const stream = await navigator.mediaDevices.getUserMedia({
        video: {facingMode: 'user'}
    });
    video.srcObject = stream;

    // Waiting for the video to be ready
    await new Promise(resolve => {
        video.onloadmetadata = () => {
            video.width = video.innerWidth;
            video.height = video.innerHeight;
            resolve();
        };
    });

    // Creating Video Texture
    videoTexture = new THREE.VideoTexture(video);
}

// Loading ML Models
async function loadModels()
{
    poseDetector = await poseDetection.createDetector(
        poseDetection.SupportedModels.MoveNet,
        {
            modelType: poseDetection.movenet.modelType.SINGLEPOSE_THUNDER,
            enableTracking: true
        }
    );

    bodySegmenter = await bodySegmentation.createSegmenter(
        bodySegmentation.SupportedModels.MediaPipeSelfieSegmentation,
        {
            runtime: 'mediapipe',
            modelType: 'general',
            solutionPath: 'https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation'
        }
    );

    isModelsLoaded = true;
    document.getElementById('loading').style.display = 'none';
}


