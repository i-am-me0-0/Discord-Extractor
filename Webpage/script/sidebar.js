class CustomSidebar extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });  // Attach shadow DOM
    }

    connectedCallback() {
        this.render();
    }

    render() {
        this.shadowRoot.innerHTML = `
        <style>
            :host {
                display: block;
                width: 250px;
                background: #1E2124;
                height: 100vh;
                padding: 20px;
                box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            a {
                text-decoration: none;
                display: block;
                padding: 10px;
                margin: 10px 0;
                font-size: 18px;
                border-radius: 5px;
                background: #7289DA;
                color: white;
                text-align: center;
                font-weight: bold;
                transition: background 0.3s;
                width: 100%;
            }
            a:hover { background: #5b6eae; }
            p {
                font-size: 14px;
                color: #B9BBBE;
                text-align: center;
                margin-top: 5px;
                margin-bottom: 15px;
            }
        </style>
        <a href="./index.html">Fetch</a> 
        <p>Fetches a sticker based on the sticker ID and displays it.</p>
        
        <a href="./convert.html" >Convert</a> <!--use target="_blank" to open in new window-->
        <p>Converts an APNG to GIF via FFmpeg, provide a link to the file or upload the file and FFmpeg will convert it, then allows downloading the created GIF.</p>

        <a href="./gallery.html">Gallery</a>
        <p>Displays all saved images dynamically from the server.</p>



        <a href="./combined-lottie.html" >Lottie</a>
        <p>Fetches a Lottie file based on the sticker ID and caches the Lottie file then displays it, to do conversion to GIF or APNG of the cached file.</p>
        
        `;
    }
}

// Define the custom element
customElements.define('custom-sidebar', CustomSidebar);
