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
