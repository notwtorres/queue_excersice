let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

const recordButton = document.getElementById('recordButton');
const micButton = document.getElementById('micButton');
const transcriptionDiv = document.getElementById('transcription');
const queueList = document.getElementById('queueList');

function updateQueue(queue) {
    queueList.innerHTML = '';
    if (queue.length === 0) {
        queueList.innerHTML = '<li>No names in queue</li>';
    } else {
        queue.forEach(name => {
            const li = document.createElement('li');
            li.textContent = name;
            queueList.appendChild(li);
        });
    }
}

async function fetchQueue() {
    try {
        const response = await fetch('/queue');
        const result = await response.json();
        updateQueue(result.queue);
    } catch (error) {
        console.error('Failed to fetch queue:', error);
    }
}

// Initial queue load
fetchQueue();

recordButton.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const webmBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('audio', webmBlob, 'recording.webm');

                try {
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    if (result.error) {
                        transcriptionDiv.textContent = `Error: ${result.error}`;
                    } else {
                        transcriptionDiv.textContent = `Transcribed: ${result.text}`;
                        updateQueue(result.queue);
                    }
                    console.log("✅ Transcription result:", result);
                } catch (error) {
                    transcriptionDiv.textContent = 'Request failed: ' + error.message;
                }
            };

            mediaRecorder.start();
            recordButton.textContent = 'Stop Recording';
            recordButton.classList.add('recording');
            isRecording = true;
        } catch (err) {
            transcriptionDiv.textContent = 'Microphone access error: ' + err.message;
        }
    } else {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
        recordButton.classList.remove('recording');
        isRecording = false;
    }
});

micButton.addEventListener('click', async () => {
    if (!micButton.classList.contains('recording')) {
        micButton.textContent = 'Stop Recording';
        micButton.classList.add('recording');
        try {
            const response = await fetch('/mic_transcribe', {
                method: 'POST'
            });
            const result = await response.json();
            if (result.error) {
                transcriptionDiv.textContent = `Error: ${result.error}`;
            } else {
                transcriptionDiv.textContent = `Transcribed: ${result.text}`;
                updateQueue(result.queue);
            }
            console.log("✅ Microphone transcription result:", result);
        } catch (error) {
            transcriptionDiv.textContent = 'Microphone transcription error: ' + error.message;
        } finally {
            micButton.textContent = 'Record with Microphone';
            micButton.classList.remove('recording');
        }
    }
});


