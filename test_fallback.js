const https = require('https');
https.get('https://api.themoviedb.org/3/movie/682110?api_key=a371649908276cdfd4448c0585638a77&language=pt-PT&append_to_response=translations', (res) => {
    let body = '';
    res.on('data', c => body += c);
    res.on('end', () => {
        const data = JSON.parse(body);
        const en = data.translations.translations.find(t => t.iso_639_1 === 'en');
        console.log(JSON.stringify(en.data, null, 2));
    });
});
