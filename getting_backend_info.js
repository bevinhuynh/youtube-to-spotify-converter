const redirect_uri = 'http://localhost:1410/open-browser';

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
    try {
        const response = await fetch('http://localhost:1410/start-convert')
        if (response.ok){
            let header = document.getElementById("header")
            header.innerHTML = "lol";
        }
    }
    catch {
        let header = document.getElementById("header")
        header.innerHTML = "lol";
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