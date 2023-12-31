import streamlit as st
from audiorecorder import audiorecorder
from gradio_client import Client
import base64
import json
import time
import os

# Page configuration
st.set_page_config(page_title="Sema STT", page_icon="🎙️", layout="wide",)

# CSS styling to center the spinner
st.markdown(
    """
    <style>
    .stSpinner {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(+0%, -50%);
        z-index: 9999;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ASR_LANGUAGES = {}
with open(f"/mount/src/semanapdf/docs/all_langs.tsv") as f:
    for line in f:
        iso, name = line.strip().split(" ", 1)
        ASR_LANGUAGES[name] = iso


def perform_speech_to_text(audio_file_path, language=None):
    try:
        if language:
            iso = language
        else:
            default_lang = "eng"
            client1 = Client("https://mms-meta-mms.hf.space/")
            lang_code = client1.predict(
                None,
                audio_file_path,
                None,
                api_name="/predict_2"  # language Identification
            )
            file_path = lang_code

            with open(file_path, "r") as file:
                data = json.load(file)
            language = data['label'].strip().replace(" ", "")
            iso = default_lang or ASR_LANGUAGES.get(language)
            # print(data['label'])
            # st.write(language)

        time.sleep(1)
        client2 = Client("https://mms-meta-mms.hf.space/")
        transcription = client2.predict(
            None,
            audio_file_path,
            None,
            iso,
            api_name="/predict"  # Speech to text
        )
        # st.write(language, transcription)
        return language, transcription

    except Exception as e:
        # Handle the exception here
        st.error(f"An error occurred: {str(e)}")
        return None, None  

result = ''

html_code = """
<!DOCTYPE html>
<html>

<head>
<style>
body {
    background-color: transparent;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 70vh; // position on screen
}
#visualizer-container {
    position: relative;
    width: 200px;
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
}

</style>
<title>
Creating an audio visualizer
using HTML CANVAS API
</title>
</head>

<body>
<div id="visualizer-container">
<canvas id="visualizer" width="1500px"
    height="150px"> // Shape
</canvas>
</div>

<script type="text/javascript">
document.addEventListener("DOMContentLoaded", async () => {
    let stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false
    });

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const mediaStreamSource =
        audioContext.createMediaStreamSource(stream);

    // Connecting the analyzer to the media source
    mediaStreamSource.connect(analyser);
    analyser.fftSize = 256;
    drawVisualizer();

    function drawVisualizer() {
        requestAnimationFrame(drawVisualizer)
        const bufferLength = analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)

        // Updating the analyzer with the new
        // generated data visualization
        analyser.getByteFrequencyData(dataArray)
        const width = visualizer.width
        const height = visualizer.height
        const barWidth = 3 // Adjust bar width here
        const centerX = width / 2; // Calculate center X
        const centerY = height / 2; // Calculate center Y
        const canvasContext = visualizer.getContext('2d')
        canvasContext.clearRect(0, 0, width, height)
        let x = -barWidth // Start x at -barWidth to remove gap
        dataArray.forEach((item, index, array) => {

            // This formula decides the height of the vertical
            // lines for every item in dataArray
            const y = item / 255 * height * 0.45; // Adjusted for reflection effect
            canvasContext.strokeStyle = `orange`

            // This decides the distances between the
            // vertical lines
            x = x + barWidth
            canvasContext.beginPath();
            canvasContext.lineCap = "round";
            canvasContext.lineWidth = 2;

            // Reflect on the top and bottom as well as left and right
            canvasContext.moveTo(centerX + x, centerY + y);
            canvasContext.lineTo(centerX + x, centerY - y);
            canvasContext.moveTo(centerX - x, centerY + y);
            canvasContext.lineTo(centerX - x, centerY - y);

            canvasContext.stroke();
        })
    }
});
</script>
</body>

</html>
"""


def transcribe():
    style = "<style>.row-widget.stButton {text-align: center;}</style>"
    with st.chat_message("user"):
        audio = audiorecorder("Talk to Sema", "Listening...")
        print(type(audio))
        st.components.v1.html(html_code, height=200)
        if len(audio) > 0:
            # To save audio to a file:
            current_directory = os.getcwd()
            audio.export("audio.wav", format="wav")
            st.audio("audio.wav")  # Use quotes around the file name
            #st.info(f"Path: {current_directory}/audio.wav")
    with st.chat_message("assistant"):
        try:
            result = perform_speech_to_text("/mount/src/semanapdf/audio.wav", )
            #print(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
        except:
            result = "Speak / Allow Microphone"
        st.info(result)
    # Delete the audio file
    try:
        os.remove("/mount/src/semanapdf/audio.wav")
    except Exception as e:
        st.warning(f"Failed to delete audio file: {str(e)}")

if __name__ == '__main__':
    print("Multilingual Transcriber")
    transcribe()
