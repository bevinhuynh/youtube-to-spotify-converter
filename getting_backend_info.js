const redirect_uri = 'http://localhost:1410/open-browser';

let data = {
    playlist_url: ''
}

async function handle_authorization() {
    try {
        const response = await fetch('http://localhost:1410/open-browser', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        // If the response is a redirect, navigate the browser to the new URL
        if (response.ok) {
            chrome.tabs.create({ url: response.url });
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


async function handle_playlist_creation() {
    let input_data = document.getElementById("input-box");
    let input_value = input_data.value;
    let subtitle = document.getElementById("subtitle")
    if (input_value.includes("youtube.com/playlist?list=")) {
        data.playlist_url = input_value;
        try {
            subtitle.textContent = "Please paste in a valid YouTube playlist link."
            const response = await fetch('http://localhost:1410/start-convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data.playlist_url)
            })

        }
        catch {
            subtitle.textContent = "Error occured with playlist conversion.";
        }
    }
    else {
        subtitle.textContent = "Invalid playlist link.";
    }
}

async function handle_youtube_authorization() {
    const response = await fetch('http://localhost:1410/youtube-auth',{
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })

}


document.getElementById("youtube-auth").addEventListener("click", function(){
    handle_youtube_authorization();
})


document.getElementById("convert").addEventListener("click", function() {
    handle_playlist_creation();
})

document.getElementById("start").addEventListener("click", function() {
    handle_authorization();
})